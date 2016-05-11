#!/bin/bash -x
date
# check everything is set...
if [ "${CONNECTSTRING}" == "" ] || [ "${TENANT}" == "" ]; then
    echo "CONNECTSTRING, TENANT and/or CORE environment variables are not set. Did you edit set-env.sh and 'source set-env.sh'?"
    exit
fi
##############################################################################
# run the "media query" (media results are shared by all other cores)
# cleanup newlines and crlf in data, then switch record separator.
##############################################################################
time psql -F $'\t' -R"@@" -A -U $USERNAME -d "$CONNECTSTRING" -f ${TENANT}.media.sql | perl -pe 's/[\r\n]/ /g;s/\@\@/\n/g' > 4solr.$TENANT.media.csv
for CORE in public internal
do
  ##############################################################################
  # copy the current set of extracts to temp (thereby saving the previous run, just in case)
  ##############################################################################
  cp 4solr.${TENANT}.${CORE}.csv.gz /tmp
  ##############################################################################
  # extract metadata and media info from CSpace
  # cleanup newlines and crlf in data, then switch record separator.
  ##############################################################################
  # start the stitching process: extract the "basic" data
  ##############################################################################
  time psql -F $'\t' -R"@@" -A -U $USERNAME -d "$CONNECTSTRING" -f ${TENANT}.${CORE}.sql | perl -pe 's/[\r\n]/ /g;s/\@\@/\n/g' > ${TENANT}.${CORE}.csv
  ##############################################################################
  # check that all rows have the same number of fields as the header
  export NUMCOLS=`grep csid ${TENANT}.${CORE}.csv | awk '{ FS = "\t" ; print NF}'`
  time awk -v NUMCOLS=$NUMCOLS '{ FS = "\t" ; if (NF == 0+NUMCOLS) print }' ${TENANT}.${CORE}.csv | perl -pe 's/\\/\//g;s/\t"/\t/g;s/"\t/\t/g;' > 4solr.$TENANT.base.${CORE}.csv &
  time awk -v NUMCOLS=$NUMCOLS '{ FS = "\t" ; if (NF != 0+NUMCOLS) print }' ${TENANT}.${CORE}.csv | perl -pe 's/\\/\//g' > errors.${CORE}.csv &
  wait
  # merge media and metadata files (done in perl ... very complicated to do in SQL)
  time perl mergeObjectsAndMedia.pl 4solr.$TENANT.media.csv 4solr.$TENANT.base.${CORE}.csv > d6.csv
  # recover the solr header and put it back at the top of the file
  grep csid d6.csv > header4Solr.csv
  #perl -i -pe 's/$/blob_ss/;' header4Solr.csv
  # generate solr schema <copyField> elements, just in case.
  # also generate parameters for POST to solr (to split _ss fields properly)
  ./genschema.sh ${CORE}
  grep -v csid d6.csv > d8.csv
  cat header4Solr.csv d8.csv | perl -pe 's/␥/|/g' > 4solr.$TENANT.${CORE}.csv
  # clean up some outstanding sins perpetuated by earlier scripts
  perl -i -pe 's/\r//g;s/\\/\//g;s/\t"/\t/g;s/"\t/\t/g;s/\"\"/"/g' 4solr.$TENANT.${CORE}.csv
  ##############################################################################
  # ok, now let's load this into solr...
  # clear out the existing data
  ##############################################################################
  curl -S -s "http://localhost:8983/solr/${TENANT}-${CORE}/update" --data '<delete><query>*:*</query></delete>' -H 'Content-type:text/xml; charset=utf-8'
  curl -S -s "http://localhost:8983/solr/${TENANT}-${CORE}/update" --data '<commit/>' -H 'Content-type:text/xml; charset=utf-8'
  ##############################################################################
  # this POSTs the csv to the Solr / update endpoint
  # note, among other things, the overriding of the encapsulator with \
  ##############################################################################
  ss_string=`cat uploadparms.${CORE}.txt`
  time curl -S -s "http://localhost:8983/solr/${TENANT}-${CORE}/update/csv?commit=true&header=true&separator=%09&${ss_string}f.blob_ss.split=true&f.blob_ss.separator=,&encapsulator=\\" --data-binary @4solr.$TENANT.${CORE}.csv -H 'Content-type:text/plain; charset=utf-8'
  time bash evaluate.sh 4solr.$TENANT.${CORE}.csv > 4solr.fields.$TENANT.${CORE}.csv
  # make a provisional field definitions file
  cut -f2 4solr.fields.$TENANT.${CORE}.csv | perl createfielddefs.pl $TENANT ${CORE} > $TENANT${CORE}parms.csv
  # zip up .csvs, save a bit of space on disk
  gzip -f 4solr.${TENANT}.${CORE}.csv
done
#
date
