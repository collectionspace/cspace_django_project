__author__ = 'jblowe'

import operator

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, HttpResponse
from django import forms
import json

from utils import loginfo, dispatch, appLayout, setconstants, APPS

@login_required()
def index(request):
    # APPS is a dict of configured webapps, show the list sorted by "app title"
    sorted_apps = sorted(APPS.items(), key=operator.itemgetter(1))
    context = setconstants(request, {'apps': sorted_apps}, 'listapps')
    return render(request, 'toolbox.html', context)


@login_required()
def tool(request, appname):
    # if we are here, we have been given a particular appname, e.g. "keyinfo", as part of the url
    context = {'applayout': appLayout[appname]}
    if request.method == 'POST':
        form = forms.Form(request.POST)

    elif request.method == 'GET':
        form = forms.Form(request.GET)

    else:
        form = forms.Form()

    if form.is_valid():
        loginfo(appname, context, request)
        context = dispatch(context, request, appname)

        #context['form'] = form
        context = setconstants(request, context, appname)
        loginfo(appname, context, request)

    # special case: the data endpoint returns JSON
    if appname == 'data':
        return HttpResponse(json.dumps(context['data']))
    else:
        return render(request, 'toolbox.html', context)
