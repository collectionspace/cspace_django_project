import os

# settings needed for Production

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_PARENT_DIR = os.path.dirname(BASE_DIR)
LOGS_DIR = BASE_PARENT_DIR + os.sep + 'logs'
PROJECT_NAME = os.path.basename(BASE_PARENT_DIR)
GOOGLE_ANALYTICS = 1

CACHES = {
   'default': {
       'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
       'LOCATION': '/home/app_webapps/cache/' + PROJECT_NAME + '/images',
       'CULL_FREQUENCY': 100000,
       'OPTIONS': {
           'MAX_ENTRIES': 1000000
       }
   }
}

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
