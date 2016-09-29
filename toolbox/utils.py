import re
import time
import os
import ConfigParser
import csv
import logging

from common import cspace  # we use the config file reading function
from common.utils import devicetype
from cspace_django_site import settings
from .models import AdditionalInfo

import heavylifting, constants

# Get an instance of a logger, log some startup info
logger = logging.getLogger(__name__)
logger.info('%s :: %s :: %s' % ('toolbox startup', '-', '-'))


def getdropdown(dropdown):

    form = {'institution': institution}
    if dropdown == 'tricoderusers': return constants.tricoderUsers()
    elif dropdown == 'handlers': return constants.getHandlers(form)
    elif dropdown == 'reasons': return constants.getReasons(form)
    elif dropdown == 'printers': return constants.getPrinters(form)
    elif dropdown == 'fieldset': return constants.getFieldset(form)
    elif dropdown == 'hierarchies': return constants.getHierarchies(form)
    elif dropdown == 'altnumtypes': return constants.getAltNumTypes(form)
    elif dropdown == 'objtype': return constants.getObjType(form)
    elif dropdown == 'collman': return constants.getCollMan(form)
    elif dropdown == 'agencies': return constants.getAgencies(form)
    elif dropdown == 'activities': return constants.getActivities(form)
    elif dropdown == 'periods': return constants.getPeriods(form)

    return '',''


def convert2int(s):
    try:
        return int(s)
    except ValueError:
        return s


def loginfo(infotype, context, request):
    logdata = ''
    # user = getattr(request, 'user', None)
    if request.user and not request.user.is_anonymous():
        username = request.user.username
    else:
        username = '-'
    if 'count' in context:
        count = context['count']
    else:
        count = '-'
    if 'querystring' in context:
        logdata = context['querystring']
    if 'url' in context:
        logdata += ' :: %s' % context['url']
    logger.info('%s :: %s :: %s :: %s' % (infotype, count, username, logdata))


def setconstants(request, context, appname):
    context['timestamp'] = time.strftime("%b %d %Y %H:%M:%S", time.localtime())
    context['searchrows'] = range(1, 4)
    context['searchcolumns'] = range(1, 4)
    context['apptitle'] = APPS[appname][0]
    context['appname'] = appname
    context['suggestions'] = suggestions
    context['institution'] = institution
    context['version'] = VERSION
    context['additionalInfo'] = AdditionalInfo.objects.filter(live=True)
    context['device'] = devicetype(request)

    return context


def getfromXML(element, xpath):
    result = element.find(xpath)
    if result is None: return ''
    result = '' if result.text is None else result.text
    result = re.sub(r"^.*\)'(.*)'$", "\\1", result)
    return result


def dispatch(context, request, appname):

    # data requests are special (render json, not html)
    if appname == 'data':
        context = heavylifting.getData(context, request)

    else:
        # do the heavy lifting
        if 'search' in request.POST:
            context = heavylifting.doSearch(context, request)
        elif 'review' in request.POST:
            context = heavylifting.doReview(context, request)
        elif 'enumerate' in request.POST:
            context = heavylifting.doEnumerate(context, request)
        elif 'update' in request.POST:
            context = heavylifting.doUpdate(context, request)
        elif 'movecheck' in request.POST:
            context = heavylifting.doMovecheck(context, request)
        elif 'save' in request.POST:
            context = heavylifting.doSave(context, request)
        elif 'activity' in request.POST:
            context = heavylifting.doActivity(context, request)

    return context


def getapplist(myappdir, thisInstitution, thisDeployment):
    files = os.listdir(myappdir)
    badconfigfiles = []

    webapps = {'listapps': ['Available Tools', 'red', None, 'green']}

    for configfile in files:
        if '.cfg' in configfile:
            config = ConfigParser.RawConfigParser()
            config.read(os.path.join(myappdir, configfile))
            try:
                deployment = config.get('info', 'serverlabel')
                institution = config.get('info', 'institution')
                # only show options for this deployment and institution ignore other config files
                if deployment != thisDeployment or institution != thisInstitution:
                    continue
                logo = config.get('info', 'logo')
                updateType = config.get('info', 'updatetype')
                schemacolor1 = config.get('info', 'schemacolor1')
                institution = config.get('info', 'institution')
                apptitle = config.get('info', 'apptitle')
                serverlabelcolor = config.get('info', 'serverlabelcolor')
                webapps[updateType] = [apptitle, serverlabelcolor, configfile, schemacolor1, logo]
            except:
                badconfigfiles.append(configfile)

    if badconfigfiles != []:
        webapps['badconfigfiles'] = badconfigfiles

    return webapps


def definefields(parmFile, suggestions):
    columns = "id app name label type parameter autocomplete row column".split(" ")

    try:
        f = open(parmFile, 'rb')
        csvfile = csv.reader(f, delimiter="\t")
    except IOError:
        raise
        message = 'Expected to be able to read %s, but it was not found or unreadable' % parmFile
        return message, -1
    except:
        raise

    try:
        appLayout = {}
        for row in csvfile:
            if row[0] == '': continue
            if row[0][0] == '#': continue
            app = row[1]
            if suggestions == 'postgres' and row[6] != '':
                varname = '%s.%s' % (row[6], row[2])
            else:
                varname = row[2]
            if not app in appLayout:
                appLayout[app] = {}
            if not varname in appLayout[app]:
                appLayout[app][varname] = {}
            for r, v in enumerate(row):
                appLayout[app][varname][columns[r]] = convert2int(row[r])
            if row[4] == 'dropdown':
                appLayout[app][varname][columns[5]] = getdropdown(row[5])

        f.close()

        return appLayout

    except IOError:
        message = 'Could not read (or maybe parse) rows from %s' % parmFile
        return message, -1
    except:
        raise


# global variables

config = cspace.getConfig(os.path.join(settings.BASE_PARENT_DIR, 'config'), 'toolbox')
APPDIR = os.path.join(settings.BASE_PARENT_DIR, 'toolbox', config.get('info', 'appdir'))
institution = config.get('info', 'institution')
deployment = config.get('info', 'serverlabel')
APPS = getapplist(APPDIR, institution, deployment)
try:
    suggestions = config.get('connect', 'suggestions')
except:
    suggestions = None

appLayout = definefields(os.path.join(settings.BASE_PARENT_DIR, 'toolbox', APPDIR, 'layout.csv'), suggestions)

try:
    VERSION = os.popen("cd " + settings.BASE_PARENT_DIR + " ; /usr/bin/git describe --always").read().strip()
    if VERSION == '':  # try alternate location for git (this is the usual Mac location)
        VERSION = os.popen("/usr/local/bin/git describe --always").read().strip()
except:
    VERSION = 'Unknown'
