# Django settings for cspace_django_site project.
import os
import logging

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_PARENT_DIR = os.path.dirname(BASE_DIR)
LOGS_DIR = BASE_PARENT_DIR + os.sep + 'logs'
PROJECT_NAME = os.path.basename(BASE_PARENT_DIR)

try:
    from extra_settings import *
except ImportError, exp:
    print 'you must configure one of the extra_*.py settings files as extra_settings.py!'
    exit(0)

DEBUG = True
TEMPLATE_DEBUG = DEBUG

import django.conf.global_settings as DEFAULT_SETTINGS  # http://stackoverflow.com/a/15446953/1763984
TEMPLATE_CONTEXT_PROCESSORS = DEFAULT_SETTINGS.TEMPLATE_CONTEXT_PROCESSORS + (
    'django.core.context_processors.request',
    'cspace_django_site.context_processors.settings',
)

ADMINS = (
    # ('Your Name', 'your_email@intakes.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': BASE_PARENT_DIR + os.sep + 'db.sqlite3',  # Or path to database file if using sqlite3.
        # The following settings are not used with sqlite3:
        'USER': '',
        'PASSWORD': '',
        'HOST': '',              # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '',              # Set to empty string for default.
    }
}

REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ]
}

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = []

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'America/Los_Angeles'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/intakes.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://intakes.com/media/", "http://media.intakes.com/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/intakes.com/static/"
STATIC_ROOT = os.path.join(BASE_DIR, '../static_root')

# URL prefix for static files.
# Example: "http://intakes.com/static/", "http://static.intakes.com/"
STATIC_URL = '/' + PROJECT_NAME + '_static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(BASE_DIR, 'static'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    #'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
#SECRET_KEY = 'createdatruntime.see.secret_key_gen'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    #'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'mobileesp.middleware.MobileDetectionMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'cspace_django_site.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'cspace_django_site.wsgi.application'

TEMPLATE_DIRS = [os.path.join(BASE_DIR, 'templates'), os.path.join(BASE_DIR, 'common/templates')]

#TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
#)



# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
# noinspection PyUnresolvedReferences
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'root': {
        'level': 'DEBUG',
        'handlers': ['console', 'logfile'],
    },
    'formatters': {
        'standard': {
            'format': "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'logfile': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOGS_DIR + os.sep + 'logfile.txt',
            'maxBytes': 10000000,
            'backupCount': 5,
            'formatter': 'standard',
        },
        'console': {
            'level': 'WARNING',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'WARNING',
            'propagate': True,
        },
    }
}

#
# Log things from this file only to a separate "settings.log" file.
#
logging.basicConfig(filename=LOGS_DIR + os.sep + 'settings.log', level=logging.DEBUG)
logging.debug('Settings log file started.')

#
# If the application's WSGI setup script added an environment variable to tell us
# the WSGI mount point path then we should use it; otherwise, we'll assume that
# the application was mounted at the root of the current server
#
WSGI_BASE = os.environ.get(__package__ + ".WSGI_BASE")
if WSGI_BASE is not None:
    logging.debug('WSGI_BASE was found in environment variable: ' + __package__ + ".WSGI_BASE")
else:
    logging.debug('WSGI_BASE was not set.')
    WSGI_BASE = ''

logging.debug('WSGI_BASE =' + WSGI_BASE)
LOGIN_URL = WSGI_BASE + '/accounts/login'
LOGIN_REDIRECT_URL = WSGI_BASE + '/landing'

#
# AuthN backends
#
# noinspection PyUnresolvedReferences
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'authn.authn.CSpaceAuthN',
)

try:
    from secret_key import *
except ImportError:
    SETTINGS_DIR=os.path.abspath(os.path.dirname(__file__))
    from secret_key_gen import *
    generate_secret_key(os.path.join(SETTINGS_DIR, 'secret_key.py'))
    from secret_key import *
