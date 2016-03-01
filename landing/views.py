__author__ = 'jblowe'

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, HttpResponse
import json
from django.conf import settings
from os import path

from cspace_django_site.main import cspace_django_site
from common import cspace

config = cspace_django_site.getConfig()
hostname = cspace.getConfigOptionWithSection(config,
                                             cspace.CONFIGSECTION_AUTHN_CONNECT,
                                             cspace.CSPACE_HOSTNAME_PROPERTY)

TITLE = 'Applications Available'

landingConfig = cspace.getConfig(path.join(settings.BASE_PARENT_DIR, 'config'), 'landing')
hiddenApps = landingConfig.get('landing', 'hiddenApps').split(',')
loginRequiredApps = landingConfig.get('landing', 'loginRequiredApps').split(',')


def getapplist(request):
    appList = [app for app in settings.INSTALLED_APPS if not "django" in app and not app in hiddenApps]

    appList.sort()
    appList = [(app,path.join(settings.WSGI_BASE, app)) for app in appList]
    return appList


def index(request):
    appList = getapplist(request)
    if not request.user.is_authenticated():
        appList = [app for app in appList if not app[0] in loginRequiredApps]
    return render(request, 'listApps.html',
                  {'appList': appList, 'labels': 'name file'.split(' '), 'apptitle': TITLE, 'hostname': hostname})


def applist(request):
    appList = getapplist(request)
    if 'publiconly' in request.GET:
            appList = [app for app in appList if not app[0] in loginRequiredApps]
    return HttpResponse(json.dumps(appList))
