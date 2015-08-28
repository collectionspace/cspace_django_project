import os
import sys
import django.core.handlers.wsgi

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BASE_DIR)
PROJECT_NAME = os.path.basename(PROJECT_DIR)
 
if PROJECT_DIR not in sys.path:
    sys.path.append(PROJECT_DIR)
 
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cspace_django_site.settings")

#
# By setting a WSGI_BASE value in the environment, the target application
# can detect the path for the WSGI's Apache mount point.  This value must
# correspond the the value used to set Apache's WSGIScriptAlias mount point.
#
WSGI_BASE = '/%s' % PROJECT_NAME
os.environ.setdefault("cspace_django_site.WSGI_BASE", WSGI_BASE)
 
application = django.core.handlers.wsgi.WSGIHandler()
