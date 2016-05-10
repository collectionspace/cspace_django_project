if [ ! -f start.jar ];
then
   echo "no start.jar here. can't start solr. are you in the right directory?"
   exit 1
fi
if [ -d nohup.out ];
then
   rm nohup.out
fi
# start solr and run it in the background...512MB is good enough for most development purposes
nohup java -Dsolr.solr.home=multicore -Xmx512m -jar start.jar &
echo "Solr starting up..."
echo
echo "check your Solr4 admin console at http://localhost:8983/solr/"

