__author__ = 'jblowe'

from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import json
#from common.cspace import logged_in_or_basicauth
from django.shortcuts import render, HttpResponse, redirect
from django.core.servers.basehttp import FileWrapper
#from django.conf import settings
#from django import forms
from os import path
import time, datetime
from getNumber import getNumber
from utils import SERVERINFO, POSTBLOBPATH, INSTITUTION, getDropdowns, handle_uploaded_file, assignValue,  get_exif, writeCsv, \
    getJobfile, getJoblist, loginfo, getQueue
import subprocess

TITLE = 'Bulk Media Upload'

overrides = [['ifblank', 'Overide only if blank'],
             ['always', 'Always Overide']]


class im:  # empty class for image metadata
    pass


def prepareFiles(request, validateonly, dropdowns):
    jobinfo = {}
    images = []
    for lineno, afile in enumerate(request.FILES.getlist('imagefiles')):
        # print afile
        try:
            print "%s %s: %s %s (%s %s)" % ('id', lineno, 'name', afile.name, 'size', afile.size)
            image = get_exif(afile)
            filename, objectnumber, imagenumber = getNumber(afile.name, INSTITUTION)
            # objectCSID = getCSID(objectnumber)
            im.creator, im.creatorRefname = assignValue(im.creatorDisplayname, im.overrideCreator, image, 'Artist',
                                                        dropdowns['creators'])
            im.contributor, dummy = assignValue(im.contributor, im.overrideContributor, image, 'ImageDescription', {})
            im.rightsholder, im.rightsholderRefname = assignValue(im.rightsholderDisplayname, im.overrideRightsholder,
                                                                  image, 'RightsHolder', dropdowns['rightsholders'])
            datetimedigitized, dummy = assignValue('', 'ifblank', image, 'DateTimeDigitized', {})
            imageinfo = {'id': lineno, 'name': afile.name, 'size': afile.size,
                         'objectnumber': objectnumber,
                         'imagenumber': imagenumber,
                         # 'objectCSID': objectCSID,
                         'date': datetimedigitized,
                         'creator': im.creatorRefname,
                         'contributor': im.contributor,
                         'rightsholder': im.rightsholderRefname,
                         'creatorDisplayname': im.creator,
                         'rightsholderDisplayname': im.rightsholder,
                         'contributorDisplayname': im.contributor
            }
            if not validateonly:
                handle_uploaded_file(afile)

            for option in ['handling', 'approvedforweb']:
                if option in request.POST:
                    imageinfo[option] = request.POST[option]
                else:
                    imageinfo[option] = ''

            images.append(imageinfo)
        except:
            # raise
            if not validateonly:
                # we still upload the file, anyway...
                handle_uploaded_file(afile)
            images.append({'name': afile.name, 'size': afile.size,
                           'error': 'problem extracting image metadata, not processed'})

    if len(images) > 0:
        jobnumber = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
        jobinfo['jobnumber'] = jobnumber

        if not validateonly:
            writeCsv(getJobfile(jobnumber) + '.step1.csv', images,
                     ['name', 'size', 'objectnumber', 'date', 'creator', 'contributor', 'rightsholder', 'imagenumber', 'handling', 'approvedforweb'])
        jobinfo['estimatedtime'] = '%8.1f' % (len(images) * 10 / 60.0)

        if 'createmedia' in request.POST:
            jobinfo['status'] = 'createmedia'
            if not validateonly:
                loginfo('start', getJobfile(jobnumber), request)
                try:
                    retcode = subprocess.call([path.join(POSTBLOBPATH, 'postblob.sh'), getJobfile(jobnumber)])
                    if retcode < 0:
                        loginfo('process', jobnumber + " Child was terminated by signal %s" % -retcode, request)
                    else:
                        loginfo('process', jobnumber + ": Child returned %s" % retcode, request)
                except OSError as e:
                    loginfo('error', "Execution failed: %s" % e, request)
                loginfo('finish', getJobfile(jobnumber), request)

        elif 'uploadmedia' in request.POST:
            jobinfo['status'] = 'uploadmedia'
        else:
            jobinfo['status'] = 'No status possible'

    return jobinfo, images


def setConstants(request, im):
    im.dropdowns = getDropdowns()

    im.validateonly = 'validateonly' in request.POST

    try:
        im.contributor = request.POST['contributor']
        im.overrideContributor = request.POST['overridecreator']

        im.creatorDisplayname = request.POST['creator']
        im.overrideCreator = request.POST['overridecreator']

        im.rightsholderDisplayname = request.POST['rightsholder']
        im.overrideRightsholder = request.POST['overriderightsholder']
    except:

        im.contributor = ''
        im.overrideContributor = ''

        im.creatorDisplayname = ''
        im.overrideCreator = ''

        im.rightsholderDisplayname = ''
        im.overrideRightsholder = ''

    constants = {'creator': im.creatorDisplayname, 'contributor': im.contributor,
                 'rightsholder': im.rightsholderDisplayname}

    return constants


@csrf_exempt
#@logged_in_or_basicauth()
def rest(request, action):
    elapsedtime = time.time()
    status = 'error' # assume murphy's law applies...

    if request.FILES:
        setConstants(request, im)
        jobinfo, images = prepareFiles(request, im.validateonly, im.dropdowns)
        status = 'ok' # OK, I guess it doesn't after all
    else:
        jobinfo = {}
        images = []
        status = 'no post seen' # OK, I guess it doesn't after all
        return HttpResponse(json.dumps({'status': status}))

    timestamp = time.strftime("%b %d %Y %H:%M:%S", time.localtime())
    elapsedtime = time.time() - elapsedtime

    return HttpResponse(json.dumps(
        {'status': status, 'images': images, 'jobinfo': jobinfo, 'elapsedtime': '%8.2f' % elapsedtime}), content_type='text/json')


@login_required()
def uploadfiles(request):
    elapsedtime = time.time()
    status = 'up'
    constants = setConstants(request, im)

    if request.POST:
        constants = setConstants(request, im)
        jobinfo, images = prepareFiles(request, im.validateonly, im.dropdowns)
    else:
        jobinfo = {}
        images = []
        constants = {}

    timestamp = time.strftime("%b %d %Y %H:%M:%S", time.localtime())
    elapsedtime = time.time() - elapsedtime

    return render(request, 'uploadmedia.html',
                  {'apptitle': TITLE, 'serverinfo': SERVERINFO, 'images': images, 'count': len(images),
                   'constants': constants, 'jobinfo': jobinfo, 'validateonly': im.validateonly,
                   'dropdowns': im.dropdowns, 'overrides': overrides, 'status': status, 'timestamp': timestamp,
                   'elapsedtime': '%8.2f' % elapsedtime})


@login_required()
def checkfilename(request):
    elapsedtime = time.time()
    if 'filenames2check' in request.POST and request.POST['filenames2check'] != '':
        listoffilenames = request.POST['filenames2check']
        filenames = listoffilenames.split(' ')
        objectnumbers = [getNumber(o, INSTITUTION) for o in filenames]
    else:
        objectnumbers = []
        listoffilenames = ''
    dropdowns = getDropdowns()
    elapsedtime = time.time() - elapsedtime
    status = 'up'
    timestamp = time.strftime("%b %d %Y %H:%M:%S", time.localtime())

    return render(request, 'uploadmedia.html', {'filenames2check': listoffilenames,
                                                'objectnumbers': objectnumbers, 'dropdowns': dropdowns,
                                                'overrides': overrides, 'timestamp': timestamp,
                                                'elapsedtime': '%8.2f' % elapsedtime,
                                                'status': status, 'apptitle': TITLE, 'serverinfo': SERVERINFO})


@login_required()
def showresults(request, filename):
    f = open(getJobfile(filename), "rb")
    response = HttpResponse(FileWrapper(f), content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="%s"' % filename
    return response


@login_required()
def showqueue(request):
    elapsedtime = time.time()
    jobs, errors, jobcount, errorcount = getJoblist()
    if 'checkjobs' in request.POST:
        errors = None
    elif 'showerrors' in request.POST:
        jobs = None
    else:
        jobs = None
        errors = None
        count = 0
    dropdowns = getDropdowns()
    elapsedtime = time.time() - elapsedtime
    status = 'up'
    timestamp = time.strftime("%b %d %Y %H:%M:%S", time.localtime())

    return render(request, 'uploadmedia.html',
                  {'dropdowns': dropdowns, 'overrides': overrides, 'timestamp': timestamp,
                   'elapsedtime': '%8.2f' % elapsedtime,
                   'status': status, 'apptitle': TITLE, 'serverinfo': SERVERINFO, 'jobs': jobs, 'jobcount': jobcount,
                   'errors': errors, 'errorcount': errorcount})
