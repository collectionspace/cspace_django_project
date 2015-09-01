# settings needed for Development

GOOGLE_ANALYTICS = 0

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'django_tables2',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    # 'demo' apps -- uncomment for debugging or demo
    'hello',
    'service',
    # 'service' apps: no UI
    'common',
    'suggest',
    'suggestpostgres',
    'suggestsolr',
    'batchuploadimages',
    # 'standard' apps
    #'asura',
    'imagebrowser',
    'imageserver',
    'imaginator',
    'internal',
    'ireports',
    'landing',
    'search',
    #'toolbox',
    'simplesearch',
    'uploadmedia',
    #'uploadtricoder',
)
