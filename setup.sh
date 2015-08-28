COMMAND=$1
WEBAPP=$2
if [ "$COMMAND" = "disable" ]; then
    perl -i -pe "s/('$WEBAPP')/#\1/" cspace_django_site/extra_settings.py
    perl -i -pe "s/(url)/#\1/ if /$WEBAPP/" cspace_django_site/urls.py
elif [ "$COMMAND" = "enable" ]; then
    perl -i -pe "s/#('$WEBAPP')/\1/" cspace_django_site/extra_settings.py
    perl -i -pe "s/#(url)/\1/ if /$WEBAPP/" cspace_django_site/urls.py
elif [ "$COMMAND" = "configure" ]; then
    cp cspace_django_site/extra_$2.py cspace_django_site/extra_settings.py
    cp cspace_django_site/all_urls.py cspace_django_site/urls.py
    python manage.py syncdb --noinput
    python manage.py collectstatic --noinput
    python manage.py loaddata fixtures/*
fi
