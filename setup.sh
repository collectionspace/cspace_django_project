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
    cp ~/django_example_config/$2/* config
    mv config/main.cfg cspace_django_site
    rm fixtures/*.json
    mv config/*.json fixtures
    # just to be sure, we start over with this...
    rm db.sqlite3
    python manage.py syncdb --noinput
    python manage.py migrate
    python manage.py loaddata fixtures/*.json
    cp cspace_django_site/static/cspace_django_site/images/header-logo-$2.png cspace_django_site/static/cspace_django_site/images/header-logo.png
    python manage.py collectstatic --noinput
    echo "Don't forget to configure cspace_django_site/main.cfg and the rest of the configuration files in config/"
elif [ "$COMMAND" = "configure" ]; then
    cp cspace_django_site/extra_$2.py cspace_django_site/extra_settings.py
    cp cspace_django_site/all_urls.py cspace_django_site/urls.py
    rm db.sqlite3
    python manage.py syncdb --noinput
    python manage.py migrate
    python manage.py collectstatic --noinput
fi
