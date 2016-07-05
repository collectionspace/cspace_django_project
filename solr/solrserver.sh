#!/bin/bash
#
# solr4 - Startup script for solr4
#
# chkconfig: - 86 24
# description: Solr4 server for CollectionSpace django apps
#
# processname: java

# Source function library.
#. /etc/rc.d/init.d/functions

#exit

DBGLOG=/tmp/initddbg.log
DBGFLAG=1

# the following directory may to be customized for your deployment
# you can either edit the value here, or add it to the environment variables
# SOLRDIR="/usr/local/share/solr4/xxx"
if [ ! -e "${SOLRDIR}" ];
then
   echo "${SOLRDIR} does not exist. Please set environment variable SOLRDIR and try again"
   exit 1
fi
KEY="-DSTOP.KEY=\"Requiescat\""
MEM="-Xmx512m"
JARFILE="-Dsolr.solr.home=multicore -jar start.jar"
PORT="-DSTOP.PORT=8079"
DEBUG=1
TRACEOUT='logs/solr4_trace.log'

CMD=$(echo "$1" | tr "[:upper:]" "[:lower:]")

function trace()
{
   [ $DEBUG -gt 0 ] && echo  "TRACE: $1" > $TRACEOUT
}

function msg()
{
   if [ "$1" = "exit" ]
   then
      echo >&2 "Exiting: $2"
      exit "$3"
   else
      [[ -t 0 ]]  && echo "$1"
   fi
}

function printEnv()
{
   msg $SOLRDIR
   msg $KEY
   msg $MEM
   msg 
   msg $JARFILE
   msg $PORT
}

if [ "$CMD" = "printenv" ]
then
   printEnv
   exit 0
fi

function printHelp()
{
   msg ""
   msg "  start    -- start the solr4 server in demon mode"
   msg "  stop     -- halt the solr4 server (if running in demon mode)"
   msg "  restart  -- halt (if running) and then start the solr4 server"
   msg "  startCmd -- show command string used to start the solr4 server"
   msg "  stopCmd  -- show command string used to stop the solr4 server"
   msg "  settings -- show the solr4 runtime environment variables"
   msg "  status   -- show the solr4 runtime server status"
   msg "  help     -- show this list of commandline options"
   msg ""
}

if [ "$CMD" = "" ] || [ "$CMD" = "help" ] || [ "$CMD" = "-h" ] || [ "$CMD" = "--help" ]
then
   printHelp
   exit 0
fi

function start()
{
   solrStatus="$(checkStatus)"
   if [ "$solrStatus" = "000" ]
   then
     trace "Starting Solr at `date`"
     msg "/bin/bash -c \"java $PORT $KEY $MEM $JARFILE --daemon\" " 
      /bin/bash -c "java $PORT $KEY $MEM $JARFILE --daemon"  &
   else
     msg "Solr status is \"$solrStatus\" (already running), not re-starting..."
     return 
   fi
   
   for x in {0..60}
   do
      solrStatus="$(checkStatus)"
      if [ "$solrStatus" = "000" ]
      then
         sleep 1
      else
         break
      fi
   done
   [ "$solrStatus" = "000" ] &&   msg "exit" "Unable to start solr4 - please verify that the server has been shut down cleanly." 1
   printStatus
}

function stop()
{
   if [ "$(checkStatus)" = "000" ]
   then
      msg "Solr is not running"
   else
      msg "/bin/bash -c \"java $PORT $KEY $JARFILE --stop\" "
       /bin/bash -c "java $PORT $KEY $JARFILE --stop" 
      trace "Solr stopped at `date`"
   fi
   [ "$(checkStatus)" = "000" ] || \
      msg "exit" "Solr running with status $(checkStatus), unable to shut down solr4 server" 1
   printStatus
}

function checkStatus()
{
   URL="http://localhost:8983/solr/"
   echo $(curl -I -s -o /dev/null -w "%{http_code}" "$URL")
}

function printStatus()
{
   STATUS=$(checkStatus)
   if [ "$STATUS" = "200" ]
   then
      echo "Status: Running"
   elif [ "$STATUS" = "000" ]
   then
      echo "Status: not running"
   else
      echo "Status: $STATUS"
   fi
}

[ -d "$SOLRDIR" ] && cd "$SOLRDIR"
[ `pwd` = "$SOLRDIR" ] ||  msg "exit" "Could not switch to Solr directory" 1

if [ "$CMD" = "start" ]
then
   start
elif [ "$CMD" = "stop" ]
then
   stop
elif [ "$CMD" = "restart" ]
then
   stop
   sleep 5
   start
elif [ "$CMD" = "startcmd" ]
then
   msg "/bin/bash -c \"java $PORT $KEY $MEM $JARFILE --daemon\" "
elif [ "$CMD" = "stopcmd" ]
then
   msg "/bin/bash -c \"java $PORT $KEY $JARFILE --stop\" "
elif [ "$CMD" = "status" ]
then
   printStatus
elif [ "$CMD" = "help" ] || [ "$CMD" = "-h" ] || [ "$CMD" = "--help" ]
then
   printHelp
elif [ "$CMD" = "settings" ] || [ "$CMD" = "showenv" ]
then
   printEnv
else
   trace "Got to final \"else\" clause"
   msg "exit" "No viable options" 1
fi

