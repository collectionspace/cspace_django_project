# the following configuration *should* work for most
# default postgres cspace deployments
if [ $# -lt 1 ];
then
  echo 1>&2 ""
  echo 1>&2 "source this filed with tenant name as argument!"
  echo 1>&2 ""
else
  export TENANT=$1
  export SERVER="localhost port=5432 sslmode=prefer"
  export USERNAME="reporter_$TENANT"
  export DATABASE="${TENANT}_domain_${TENANT}"
  # note that the password is not here. best practice is to
  # store it in .pgpass. 
  # if you need to set it here, add it to the CONNECT_STRING
  export CONNECTSTRING="host=$SERVER dbname=$DATABASE"
fi
