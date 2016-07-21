#!/bin/bash
#
rm -f tmp tmp2
echo "col	fieldname	types	tokens"
for w in `head -1 $1 | perl -pe "s/\|/\n/g"`
do
  ((i++))
  #extract column, split into tokens
  cut -f${i} $1 | perl -ne 's/\|/\n/g;print unless /^$/' > tmp
  types=`sort -u tmp | wc -l`
  ((types--))
  tokens=`cat tmp | wc -l`
  ((tokens--))
  echo "${i}	${w}	${types}	${tokens}" >> tmp2
done
sort -t$'\t' -k2 tmp2 | cat
rm -f tmp tmp2
