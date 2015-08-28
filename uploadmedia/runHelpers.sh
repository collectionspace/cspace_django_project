####################################################
#
# this directory contains a few "helper" scripts 
# in perl which are not (obviously) part of the
# webapp. 
#
# These scripts expect the dev/prod deployment of the
# BMU webapp on bampfa-dev to operate correctly.
#
# this shell script, while it will run, is mostly
# a demonstration of the operation of these helpers.
# 
# The two helpers examine the result of BMU operation
# and:
#
# make various reports on the jobs, e.g. how many
# media files were uploaded, how many successful
# were attached to media records and object, etc.
#
# make discrepancy reports to help users identify and
# repair failures.
#
# all very ad hoc and rickety!
#
# jblowe 2/2/2014
#
####################################################
cp /home/developers/bampfa/4solr.bampfa.media.csv media.csv
perl checkRuns.pl csids > csids.csv
perl checkObj.pl > MediaNBlobs.txt
grep OK MediaNBlobs.txt > OK.txt
grep 'NoMatch|None' MediaNBlobs.txt  | grep -v NoObjectFound> NotInDB.txt
grep NoObjectFound MediaNBlobs.txt  > NoObjectFound.txt
grep -v 'NoMatch|None' MediaNBlobs.txt  | grep -v NoObjectFound | grep -v OK> OtherIssues.txt
cut -f1 NotInDB.txt > NotInDB.jpgfilenames.txt
for f in `cat NotInDB.jpgfilenames.txt ` ; do grep  -h "$f" /tmp/upload_cache/*.step2.csv ; done | sort -u >  NotInDB.step2.csv 
for f in `cat NotInDB.jpgfilenames.txt ` ; do grep  "$f" /tmp/upload_cache/*.step2.csv ; done | sort -u > NotInDB.step2.txt  
sort -u NotInDB.step2.txt  | cut -f1 -d":" | sort | uniq -c >RerunFiles.txt
cat NoObjectFound.txt NotInDB.txt | cut -f1 > ToCheck.txt
./verifyObjectsAndMedia.sh < ToCheck.txt > ToCheck.results.txt 
perl -ne 'print if /\|\s*$/' ToCheck.results.txt > NoObjectFoundv2.txt 
wc -l *.txt
