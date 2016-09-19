#
# script to help deploy webapps
#
# essentially a type of 'make' file.
#
# the project can be set up to run in Prod, Dev, and Pycharm environments with 'configure'
# the project can be customized for any of the UCB deployments with 'deploy'
# individual webapps can be enabled and disabled
#

if [ $# -ne 2 -a "$1" != 'show' ]; then
    echo "Usage: $0 <enable|disable|deploy|redeploy|configure|show> <TENANT|CONFIGURATION|WEBAPP>"
    echo
    echo "where: TENANT = 'default' or the name of a deployable tenant"
    echo "       CONFIGURATION = <pycharm|dev|prod>"
    echo "       WEBAPP = one of the available webapps, e.g. 'search' or 'ireports'"
    echo
    echo "e.g. $0 disable ireports"
    echo "     $0 configure pycharm"
    echo "     $0 deploy botgarden"
    echo "     $0 show"
    echo
    exit
fi

COMMAND=$1
WEBAPP=$2
CURRDIR=`pwd`
CONFIGDIR=~/django_example_config

if [ "${COMMAND}" = "disable" ]; then
    perl -i -pe "s/('$WEBAPP')/#\1/" cspace_django_site/extra_settings.py
    perl -i -pe "s/(url)/#\1/ if /$WEBAPP/" cspace_django_site/urls.py
    echo "disabled $WEBAPP"
elif [ "${COMMAND}" = "enable" ]; then
    perl -i -pe "s/#* *('$WEBAPP')/\1/" cspace_django_site/extra_settings.py
    perl -i -pe "s/#* *(url)/\1/ if /$WEBAPP/" cspace_django_site/urls.py
    echo "enabled $WEBAPP"
elif [ "${COMMAND}" = "show" ]; then
    echo
    echo "Installed apps:"
    echo
    echo -e "from cspace_django_site.extra_settings import INSTALLED_APPS\nfor i in INSTALLED_APPS: print i" | python
    echo
elif [ "${COMMAND}" = "configure" ]; then
    cp cspace_django_site/extra_$2.py cspace_django_site/extra_settings.py
    cp cspace_django_site/all_urls.py cspace_django_site/urls.py
    echo
    echo "*************************************************************************************************"
    echo "OK, \"$2\" is configured. Now run ./setup.sh deploy <tenant> to set up a particular tenant,"
    echo "where <tenant> is either "default" (for non-specific tenant, i.e. nightly.collectionspace.org) or"
    echo "an existing tenant in the django_example_config repo"
    echo "*************************************************************************************************"
    echo
elif [ "${COMMAND}" = "deploy" ]; then
    if [ ! -d "${CONFIGDIR}" ]; then
        echo "the repo containing the configuration files (${CONFIGDIR}) does not exist"
        echo "please either create it (e.g. by cloning it from github)"
        echo "or edit this script to set the correct path"
        echo
        exit
    fi
    rm config/*.cfg
    rm config/*.csv
    rm config/*.xml
    rm fixtures/*.json
    if [ "$2" = "default" ]; then
        cp config.examples/* config
        cp cspace_django_site/static/cspace_django_site/images/CollectionToolzSmall.png cspace_django_site/static/cspace_django_site/images/header-logo.png
    else
        if [ ! -d "${CONFIGDIR}/$2" ]; then
            echo "can't deploy tenant $2: ${CONFIGDIR}/$2 does not exist"
            echo
            exit
        fi
        cd ${CONFIGDIR}
        git pull -v
        cd ${CURRDIR}
        cp ${CONFIGDIR}/$2/* config
        cp cspace_django_site/static/cspace_django_site/images/header-logo-$2.png cspace_django_site/static/cspace_django_site/images/header-logo.png
    fi
    mv config/main.cfg cspace_django_site
    rm fixtures/*.json
    mv config/*.json fixtures
    # just to be sure, we start over with this...
    rm db.sqlite3
    python manage.py syncdb --noinput
    # python manage.py migrate
    python manage.py loaddata fixtures/*.json
    python manage.py collectstatic --noinput
    echo
    echo "*************************************************************************************************"
    echo "Don't forget to check cspace_django_site/main.cfg if necessary and the rest of the"
    echo "configuration files in config/ (these are .cfg and .csv files)"
    echo "*************************************************************************************************"
    echo
elif [ "${COMMAND}" = "redeploy" ]; then
    cd ${CONFIGDIR}
    git pull -v
    cd ${CURRDIR}
    git checkout master
    git pull -v
    TAG=`git tag | sort -k2 -t"-" -rn | head -1`
    echo "*************************************************************************************************"
    echo ">>>> deploying $TAG"
    echo "*************************************************************************************************"
    git checkout ${TAG}
    python manage.py collectstatic --noinput
    echo
    echo "*************************************************************************************************"
    echo "restart apache to pick up changes"
    echo "*************************************************************************************************"
    echo
else
    echo "${COMMAND} is not a recognized command."
fi
