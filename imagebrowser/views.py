__author__ = 'jblowe'

import os
import re
import time
import logging

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, render_to_response

from common.utils import doSearch, setConstants, loginfo
from common.appconfig import loadConfiguration, loadFields, getParms
from common import cspace
from cspace_django_site import settings
from os import path

# read common config file
common = 'common'
prmz = loadConfiguration(common)
print 'Configuration for %s successfully read' % common

searchConfig = cspace.getConfig(path.join(settings.BASE_PARENT_DIR, 'config'), 'imagebrowser')
prmz.SOLRSERVER = searchConfig.get('imagebrowser', 'SOLRSERVER')
prmz.SOLRCORE = searchConfig.get('imagebrowser', 'SOLRCORE')
prmz.MAXRESULTS = int(searchConfig.get('imagebrowser', 'MAXRESULTS'))
prmz.TITLE = searchConfig.get('imagebrowser', 'TITLE')
prmz.FIELDDEFINITIONS = searchConfig.get('imagebrowser', 'FIELDDEFINITIONS')

# add in the the field definitions...
prmz = loadFields(prmz.FIELDDEFINITIONS, prmz)

# Get an instance of a logger, log some startup info
logger = logging.getLogger(__name__)
logger.info('%s :: %s :: %s' % ('imagebrowser startup', '-', '-'))


# @login_required()
def images(request):
    if request.method == 'GET' and request.GET != {}:
        context = {'searchValues': request.GET}

        context = setConstants(context, prmz)

        context['text'] = request.GET['text']
        #context['pgNum'] = pgNum if 'pgNum' in context else '1'
        #context['url'] = url
        context['displayType'] = 'list'
        context['pixonly'] = 'true'
        context['title'] = prmz.TITLE

        # do search
        loginfo(logger, 'start search', context, request)
        context = doSearch(context, prmz)

        return render(request, 'showImages.html', context)

    else:
        return render(request, 'showImages.html',
                      {'title': prmz.TITLE, 'pgNum': 10, 'maxresults': 20})
