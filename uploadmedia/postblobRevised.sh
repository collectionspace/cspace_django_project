#!/bin/bash

# this better be here!
source ~/www/venv/bin/activate

# three arguments required:
#
# postblob.sh tenant jobnumber configfilewithoutcfgextension
#
# e.g.
# time /var/www/ucjeps/uploadmedia/postblob.sh ucjeps 2015-11-10-09-09-09 ucjeps_Uploadmedia_Dev

TENANT=$1
RUNDIR="/var/www/${TENANT}/uploadmedia"
MEDIACONFIG="$RUNDIR/$3"
UPLOADSCRIPT="$RUNDIR/uploadMedia.py"

# this should be the fully qualified name of the input file, up to ".step1.csv"
JOB=$2
IMGDIR=$(dirname $2)

# claim this job...by renaming the input file
mv $JOB.step1.csv $JOB.inprogress.csv
INPUTFILE=$JOB.inprogress.csv
OUTPUTFILE=$JOB.step3.csv
LOGDIR=$IMGDIR
CURLLOG="$LOGDIR/curl.log"
CURLOUT="$LOGDIR/curl.out"
TRACELOG="$JOB.trace.log"

rm -f $OUTPUTFILE

TRACE=2

function trace()
{
   tdate=`date "+%Y-%m-%d %H:%M:%S"`
   [ "$TRACE" -eq 1 ] && echo "TRACE: $1"
   [ "$TRACE" -eq 2 ] && echo "TRACE: [$JOB : $tdate ] $1" >> $TRACELOG
}

trace "**** START OF RUN ******************** `date` **************************"
trace "output file: $OUTPUTFILE"

if [ ! -f "$INPUTFILE" ]
then
    trace "Missing input file: $INPUTFILE"
    echo "Missing input file: $INPUTFILE exiting..."
    exit
else
    trace "input file: $INPUTFILE"
fi
trace ">>>>>>>>>>>>>>> Starting Blob, Media, and Relation record creation process: `date` "
trace "python $UPLOADSCRIPT $INPUTFILE $MEDIACONFIG >> $TRACELOG"
python $UPLOADSCRIPT $INPUTFILE $MEDIACONFIG >> $TRACELOG 2>&1
trace "Media record and relations created."

mv $INPUTFILE $JOB.original.csv
mv $JOB.step3.csv $JOB.processed.csv

trace "**** END OF RUN ******************** `date` **************************"
