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
    cp ../django_example_config/$2/* config
    cp config/main.cfg cspace_django_site
    mv config/*.json fixtures
    cd cspace_django_site/static/cspace_django_site/images
    cp header-logo-$2.png header-logo.png
elif [ "$COMMAND" = "configure" ]; then
    cp cspace_django_site/extra_$2.py cspace_django_site/extra_settings.py
    cp cspace_django_site/all_urls.py cspace_django_site/urls.py
    python manage.py syncdb --noinput
    python manage.py collectstatic --noinput
    python manage.py loaddata fixtures/*.json
fi
echo "Don't forget to configure main.cfg and the rest of the configuration files in config/"
