#!/bin/bash
rm $1.step2.csv
rm $1.step3.csv
/usr/local/share/django/bampfa_project/uploadmedia/postblob.sh /tmp/upload_cache $1.step1.csv
#python /var/www/cgi-bin/uploadMedia.py $1.step2.csv
mv $1.step1.csv $1.original.csv
mv $1.step3.csv $1.processed.csv
