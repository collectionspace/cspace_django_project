# import site
import os
import sys
import django.core.handlers.wsgi

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BASE_DIR)
PROJECT_NAME = os.path.basename(PROJECT_DIR)
 
if PROJECT_DIR not in sys.path:
    sys.path.append(PROJECT_DIR)

# NOTE: Uncomment for, Virtual Environment (not Wrapper) deployment
# activate_env = os.path.expanduser('/usr/local/share/django/webapp/cspace_venv/bin/activate_this.py')
# execfile(activate_env, dict(__file__=activate_env))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cspace_django_site.settings")

#
# By setting a WSGI_BASE value in the environment, the target application
# can detect the path for the WSGI's Apache mount point.  This value must
# correspond the the value used to set Apache's WSGIScriptAlias mount point.
#
WSGI_BASE = '/%s' % PROJECT_NAME
os.environ.setdefault("cspace_django_site.WSGI_BASE", WSGI_BASE)

# NOTE: Comment out for Ubuntu, Apache2, production deployment
application = django.core.handlers.wsgi.WSGIHandler()

# NOTE: Uncomment lines below for Ubuntu, Apache2, production deployment
# from django.core.wsgi import get_wsgi_application
# application = get_wsgi_application()