# the following configuration *should* work for most
# default postgres cspace deployments
if [ $# -lt 1 ];
then
  echo 1>&2 ""
  echo 1>&2 "source this file with tenant name as argument!"
  echo 1>&2 ""
else
  export TENANT=$1
  export SERVER="localhost port=5432 sslmode=prefer"
  export USERNAME="reader"
  export DATABASE="nuxeo_default"
  # note that the password is not here. best practice is to
  # store it in .pgpass. 
  # if you need to set it here, add it to the CONNECT_STRING
  export CONNECTSTRING="host=$SERVER password=reader dbname=$DATABASE"
fi
