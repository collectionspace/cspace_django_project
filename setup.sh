COMMAND=$1
WEBAPP=$2
if [ "$COMMAND" = "disable" ]; then
    perl -i -pe "s/('$WEBAPP')/#\1/" cspace_django_site/extra_settings.py
    perl -i -pe "s/(url)/#\1/ if /$WEBAPP/" cspace_django_site/urls.py
elif [ "$COMMAND" = "enable" ]; then
    perl -i -pe "s/#*('$WEBAPP')/\1/" cspace_django_site/extra_settings.py
    perl -i -pe "s/#*(url)/\1/ if /$WEBAPP/" cspace_django_site/urls.py
elif [ "$COMMAND" = "show" ]; then
    echo
    echo "Installed apps:"
    echo
    echo -e "from cspace_django_site.extra_settings import INSTALLED_APPS\nfor i in INSTALLED_APPS: print i" | python
    echo
elif [ "$COMMAND" = "deploy" ]; then
    rm config/*.cfg
    rm config/*.csv
    rm config/*.xml
    if [ "$2" = "default" ]; then
        cp config.examples/* config
        cp cspace_django_site/static/cspace_django_site/images/CollectionToolzSmall.png cspace_django_site/static/cspace_django_site/images/header-logo.png
    else
        cp ~/django_example_config/$2/* config
        cp cspace_django_site/static/cspace_django_site/images/header-logo-$2.png cspace_django_site/static/cspace_django_site/images/header-logo.png
    fi
    mv config/main.cfg cspace_django_site
    rm fixtures/*.json
    mv config/*.json fixtures
    # just to be sure, we start over with this...
    rm db.sqlite3
    python manage.py syncdb --noinput
    python manage.py migrate
    python manage.py loaddata fixtures/*.json
    python manage.py collectstatic --noinput
    echo
    echo "*************************************************************************************************"
    echo "Don't forget to modify cspace_django_site/main.cfg if necessary and check on the rest of the"
    echo "configuration files in config/ (these are .cfg and .csv files)"
    echo "*************************************************************************************************"
    echo
elif [ "$COMMAND" = "configure" ]; then
    cp cspace_django_site/extra_$2.py cspace_django_site/extra_settings.py
    cp cspace_django_site/all_urls.py cspace_django_site/urls.py
    echo
    echo "*************************************************************************************************"
    echo "OK, \"$2\" is configured. Now run ./setup.sh deploy <tenant> to set up a particular tenant,"
    echo "where <tenant> is either "default" (for non-specific tenant, i.e. nightly.collectionspace.org) or"
    echo "an existing tenant in the django_example_config repo"
    echo "*************************************************************************************************"
    echo
fi
