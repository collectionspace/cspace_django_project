
read -r -d '' SQL <<'EOF'
SELECT objectNumber,
cp.sortableobjectnumber AS sortableobjectnumber,
ong.objectName AS objectname
FROM collectionobjects_common cc
left outer join collectionobjects_bampfa cp on (cp.id=cc.id)
left outer join hierarchy h4 on (cc.id = h4.parentid and h4.name =
'collectionobjects_common:objectNameList' and (h4.pos=0 or h4.pos is null))
left outer join objectnamegroup ong on (ong.id=h4.id)
INNER JOIN hierarchy h1
        ON cc.id=h1.id
INNER JOIN misc
        ON misc.id=h1.id and misc.lifecyclestate <> 'deleted'
WHERE
     cc.objectNumber = 
EOF

while read imagefile
do
  objectnumber=$(echo $imagefile| sed -e 's/_.*//')
  #SQL2=$(echo $SQL| sed -e 's/xxobjnoxx/$1/g')
  SQL2="${SQL}'$objectnumber'"
  #echo "${SQL2}"
  results=`psql -A  -t -U reporter -d "host=bampfa.cspace.berkeley.edu dbname=nuxeo password=xxxxxx" -c "$SQL2"`
  echo "$imagefile|$objectnumber|$results"|tr '\n' ' '
  echo
done
