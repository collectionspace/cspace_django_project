## Solr4 helpers for CSpace webapps

Tools (mainly shell scripts) to:
 
* deploy a multicore solr4 server on Unix-like systems (Mac, Linux, perhaps even Unix).
* load one of more solr datastores into the solr4 deployment.
* start and stop the solr service.

Currently there are 5 tools, some mature, but mostly unripe, raw, and needy:

* configureMultiCoreSolr.sh -- installs and configures the "standard" multicore configuration
* solrETL-template.sh -- an example script for extracting metadata and media data from CSpace and loading it into CSpace.
* solrserver.sh -- manage Solr4 service.
* countSolr4.sh-- if your Solr4 server is running, this script will count the records in the cores
* cleanup.sh -- gets rid of all created files
* evaluate.sh -- checks extracted files for content: count types and tokens by column
* genschema.sh -- generates bits needs by Solr.
* set-tenant-default.sh -- you'll probably need to edit this for your postgres configuration

#### Suggestions for "local installs"

e.g. on your Macbook or Ubuntu labtop, for development. Sorry, no help for Windows here!

The essence of the process. NB: the scripts _can_ do everything, but you can do it yourself too.

* Download Solr4 tarball
* Install Solr4
* Configure the multicore solr datastores
* Start the Solr4 server
* Create data extracts from one or more CSpace servers
* Verify Solr4 server works

```bash
#
# NB: if solr is *already* running, you'll need to 
#     kill it in order to start it again so it will see the new cores.
#
ps aux | grep solr
kill <thatsolrprocess>
#
# 1. Obtain the code need (mainly bash scripts) from GitHub
#
# (you'll need to clone the repo with all the goodies in it...)
# 
# let's assume that for now you'll put the solr4 data in your home directory.
cd ~
git clone https://github.com/cspace-deployment/cspace_django_project
# 
# 2. configure the Solr multicore deployment using configureMultiCoreSolr.sh
#
# NB: takes 4 arguments!
#
# run the following script which unpacks solr, makes the CollectionSpace cores, copies the customized files needed
# it also attempts to start the solr4 server
#
cd cspace_django_project/solr
./configureMultiCoreSolr.sh ~/solr4 4.10.4 topnode "tenant1 tenant2"
#
#
# 3. You should now be able to see the Solr4 admin console in your browser:
#
#    http://localhost:8983/solr/
#
#    You should have a bunch of empty solr cores named things like "tenant1-public", "tenant2-internal", etc.
# 
#    You can also check the contents of the solr server using the countSolr4.sh script:
#
./countSolr4.sh "tenant1 tenant2"
#
# 4. Now stop the solr4 server (we need to update the schema, alas)
#
ps aux | grep solr 
kill <thatsolrprocess>
#
#
# 5. To load data, you'll need to revised some queries.
#
# config a tenant
vi set-tenant-default.sh
source set-tenant-default.sh
# run the load etl
nohup ./solrETL-template.sh &
#
# You should now have some "live data" suitable for use with the Portal webapps in Solr4! Enjoy!
#
```

#### Installing solr4 as a service

```bash
# install the solr4.service script in /etc/init.d
sudo cp solr4.service /etc/init.d/solr4
# check that the script works
sudo service solr4 status
# if solr is installed as described above, the following should work
sudo service solr4 start
# you can also check if the service is running this way:
ps aux | grep java
# the logs are in the following directory:
ls -ltr /usr/local/share/solr4/topnode/logs/
# e.g.
less  /usr/local/share/solr4/topnode/logs/solr.log 
less  /usr/local/share/solr4/topnode/logs/2015_03_21-085800651.start.log 
```

#### Installing solr4 under Red Hat or Ubuntu

Both these operating system welcome user-installed sofware in /usr/local/share

The following instructions assume you'll put the solr service itself in /usr/local/share/solr4
and that you'll put the ETL code (to build and refresh the solr database) in /usr/local/share/solr-etl
and that you'll set up a cron job to run the ETL as often as needed (usually onces a night).
and that you'll do all this as root.

For example, to set up a multi-core solr service named "cspace" with a single solr core called "core"
pointing to the default CollectionSpace core tenant:

```bash
sudo su -
git clone https://github.com/cspace-deployment/cspace_django_project.git
cp -r cspace_django_project/solr solr-etl
cd solr-etl
./configureMultiCoreSolr.sh /usr/local/share/solr4 4.10.4 cspace core
./countSolr4.sh core
vi set-tenant-default.sh # only edit if your postgres service is not local and/or non-standard
source set-tenant-default.sh core ; nohup ./solrETL-template.sh
# now you'd want to add the line above to crontab
crontab -e

```
