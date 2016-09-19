__author__ = 'jblowe, amywieliczka'

import time, datetime
from os import path
import logging

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, render_to_response, redirect
from django.template.loader import render_to_string
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django import forms
from cspace_django_site.main import cspace_django_site
from common.utils import writeCsv, doSearch, setupGoogleMap, setupBMapper, computeStats, setupCSV, setup4Print, setup4PDF
from common.utils import setDisplayType, setConstants, loginfo

# from common.utils import CSVPREFIX, CSVEXTENSION
from common.appconfig import loadFields, loadConfiguration
from common import cspace  # we use the config file reading function
from .models import AdditionalInfo

from cspace_django_site import settings

# read common config file
adhocprmz = loadConfiguration('common')
print 'Configuration for common successfully read'

# on startup, setup this webapp layout...
config = cspace.getConfig(path.join(settings.BASE_PARENT_DIR, 'config'), 'adhocreports')
fielddefinitions = config.get('search', 'FIELDDEFINITIONS')
adhocprmz = loadFields(fielddefinitions, adhocprmz)
# nb: we override the app title here with the one configured for ad hoc reports
adhocprmz.TITLE = config.get('search', 'TITLE')

# Get an instance of a logger, log some startup info
logger = logging.getLogger(__name__)
logger.info('%s :: %s :: %s' % ('ad hoc reports startup', '-', '%s | %s | %s' % (adhocprmz.SOLRSERVER, adhocprmz.IMAGESERVER, adhocprmz.BMAPPERSERVER)))


def direct(request):
    return redirect('search/')


def search(request):
    if request.method == 'GET' and request.GET != {}:
        context = {'searchValues': dict(request.GET.iteritems())}
        context = doSearch(context, adhocprmz, request)

    else:
        context = setConstants({}, adhocprmz, request)

    loginfo(logger, 'start adhocreport', context, request)
    context['additionalInfo'] = AdditionalInfo.objects.filter(live=True)
    return render(request, 'adhocreports.html', context)


def retrieveResults(request):
    if request.method == 'POST' and request.POST != {}:
        requestObject = dict(request.POST.iteritems())
        form = forms.Form(requestObject)

        if form.is_valid():
            context = {'searchValues': requestObject}
            context = doSearch(context, adhocprmz, request)

            loginfo(logger, 'results.%s' % context['displayType'], context, request)
            return render(request, 'adhocresults.html', context)


def bmapper(request):
    if request.method == 'POST' and request.POST != {}:
        requestObject = dict(request.POST.iteritems())
        form = forms.Form(requestObject)

        if form.is_valid():
            context = {'searchValues': requestObject}
            context = setupBMapper(requestObject, context, adhocprmz)

            loginfo(logger, 'bmapper', context, request)
            return HttpResponse(context['bmapperurl'])


def gmapper(request):
    if request.method == 'POST' and request.POST != {}:
        requestObject = dict(request.POST.iteritems())
        form = forms.Form(requestObject)

        if form.is_valid():
            context = {'searchValues': requestObject}
            context = setupGoogleMap(requestObject, context, adhocprmz)

            loginfo(logger, 'gmapper', context, request)
            return render(request, 'maps.html', context)


def dispatch(request):

    if request.method == 'POST' and request.POST != {}:
        requestObject = dict(request.POST.iteritems())
        form = forms.Form(requestObject)

    if 'csv' in request.POST or 'downloadstats' in request.POST:

        if form.is_valid():
            try:
                context = {'searchValues': requestObject}
                csvformat, fieldset, csvitems = setupCSV(requestObject, context, adhocprmz)
                loginfo(logger, 'csv', context, request)

                # create the HttpResponse object with the appropriate CSV header.
                response = HttpResponse(content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename="%s-%s.%s"' % (
                    adhocprmz.CSVPREFIX, datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S"), adhocprmz.CSVEXTENSION)
                return writeCsv(response, fieldset, csvitems, writeheader=True, csvFormat=csvformat)
            except:
                messages.error(request, 'Problem creating .csv file. Sorry!')
                context['messages'] = messages
                return search(request)

    elif 'pdf' in request.POST:

        if form.is_valid():
            try:
                context = {'searchValues': requestObject}
                loginfo(logger, 'pdf', context, request)
                return setup4PDF(request, context, adhocprmz)

            except:
                messages.error(request, 'Problem creating .pdf file. Sorry!')
                context['messages'] = messages
                return search(request)


    elif 'preview' in request.POST:
        messages.error(request, 'Problem creating print version. Sorry!')
        context = {'messages': messages}
        return search(request)


def statistics(request):
    if request.method == 'POST' and request.POST != {}:
        requestObject = dict(request.POST.iteritems())
        form = forms.Form(requestObject)

        if form.is_valid():
            elapsedtime = time.time()
            try:
                context = {'searchValues': requestObject}
                loginfo(logger, 'statistics1', context, request)
                context = computeStats(requestObject, context, adhocprmz)
                loginfo(logger, 'statistics2', context, request)
                context['summarytime'] = '%8.2f' % (time.time() - elapsedtime)
                # 'downloadstats' is handled in writeCSV, via post
                return render(request, 'statsResults.html', context)
            except:
                context['summarytime'] = '%8.2f' % (time.time() - elapsedtime)
                return HttpResponse('Please pick some values!')


def loadNewFields(request, fieldfile, prmz):
    loadFields(fieldfile + '.csv', prmz)

    context = setConstants({}, prmz, request)
    loginfo(logger, 'loaded fields', context, request)
    return render(request, 'adhocreports.html', context)
