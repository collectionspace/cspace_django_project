#!/bin/bash

# this better be here!
source ~/venv/bin/activate

# modify these for each deployment...
PROTO="https://"
TENANT='bampfa'
HOST="${TENANT}-dev.cspace.berkeley.edu"
SRVC="cspace-services/blobs"
URL="${PROTO}${HOST}/$SRVC"
CONTENT_TYPE="Content-Type: application/xml"
USER="import@xxx.cspace.berkeley.edu:xxxxxxx"
MEDIACONFIG="/var/www/${TENANT}/uploadmedia/${TENANT}_Uploadmedia_Dev"
UPLOADSCRIPT="/var/www/${TENANT}/uploadmedia/uploadMedia.py"

# this should be the fully qualified name of the input file, up to ".step1.csv"
JOB=$1
IMGDIR=$(dirname $1)

# claim this job...by renaming the input file
mv $JOB.step1.csv $JOB.inprogress.csv
INPUTFILE=$JOB.inprogress.csv

OUTPUTFILE=$JOB.step2.csv
LOGDIR=$IMGDIR
CURLLOG="$LOGDIR/curl.log"
CURLOUT="$LOGDIR/curl.out"
TRACELOG="$JOB.trace.log"

rm -f $OUTPUTFILE
rm -f $JOB.step3.csv

TRACE=2

function trace()
{
   tdate=`date "+%Y-%m-%d %H:%M:%S"`
   [ "$TRACE" -eq 1 ] && echo "TRACE: $1"
   [ "$TRACE" -eq 2 ] && echo "TRACE: [$JOB : $tdate ] $1" >> $TRACELOG
}

trace "**** START OF RUN ******************** `date` **************************"
trace "media directory: $1"
trace "output file: $OUTPUTFILE"

if [ ! -f "$INPUTFILE" ]
then
    trace "Missing input file: $INPUTFILE"
    echo "Missing input file: $INPUTFILE exiting..."
    exit
else
    trace "input file: $INPUTFILE"
fi

while IFS='|' read -r FILENAME size objectnumber digitizedDate creator contributor rightsholder imagenumber
do
  FILEPATH="$IMGDIR/$FILENAME"

  # skip header
  if [ "$FILENAME" == "name" ]
  then
    continue
  fi

  trace ">>>>>>>>>>>>>>> Starting: $objectnumber | $digitizedDate | $FILENAME"

  if [ ! -f "$FILEPATH" ]
  then
    trace "Missing file: $FILEPATH"
    continue
  fi

  /bin/rm -f $CURLOUT

  # if filename contains commas, translate them to colons (cf CSPACE-5497)
  FILEPATH2="$FILEPATH"
  if [[ "$FILEPATH" == *,* ]]
  then
     trace "renaming $FILEPATH..."
     FILEPATH2=$(echo $FILEPATH | sed -e 's/,/:/g')
     cp "$FILEPATH" "$FILEPATH2"
  fi

  trace "curl -s -S -i -u \"xxxxx\"  --form file=\"@${FILEPATH2}\" --form press=\"OK\" \"$URL\""
  curl -s -S -i -u "$USER" --form file="@${FILEPATH2}" --form press="OK" "$URL" -o $CURLOUT

  # NB: we should someday get rid of the extra files created...

  if [ ! -f $CURLOUT ]
  then
    trace "No output file, something failed for $FILEPATH"
    continue
  fi

  if ! grep -q "HTTP/1.1 201 Created" $CURLOUT
  then
    trace "Post did not return a 201 status code for $FILEPATH"
    continue
  fi

  LOC=`grep "^Location: .*cspace-services/blobs/" $CURLOUT`
  trace "LOC $LOC"
  CSID=${LOC##*cspace-services/blobs/}
  CSID=${CSID//$'\r'}
  #trace "CSID $CSID"

  cat $CURLOUT >> $CURLLOG
  imagenumber=${imagenumber//$'\r'}
  echo "$FILENAME|$size|$objectnumber|$CSID|$digitizedDate|$creator|$contributor|$rightsholder|$imagenumber|$FILEPATH" >>  $OUTPUTFILE
done < $INPUTFILE

trace ">>>>>>>>>>>>>>> End of Blob Creation, starting Media and Relation record creation process: `date` "
trace "python $UPLOADSCRIPT $OUTPUTFILE $MEDIACONFIG >> $TRACELOG"
python $UPLOADSCRIPT $OUTPUTFILE $MEDIACONFIG >> $TRACELOG 2>&1
trace "Media record and relations created."

mv $INPUTFILE $JOB.original.csv
mv $JOB.step3.csv $JOB.processed.csv
#rm $JOB.step2.csv

trace "**** END OF RUN ******************** `date` **************************"
