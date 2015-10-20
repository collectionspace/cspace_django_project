__author__ = 'jblowe'

from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import json
#from common.cspace import logged_in_or_basicauth
from django.shortcuts import render, HttpResponse, redirect
from django.core.servers.basehttp import FileWrapper
#from django.conf import settings
#from django import forms
from os import path, remove
import logging
import time, datetime
from getNumber import getNumber
from utils import SERVERINFO, POSTBLOBPATH, INSTITUTION, BATCHPARAMETERS, FIELDS2WRITE
from utils import getBMUoptions, handle_uploaded_file, assignValue, get_exif, writeCsv, getJobfile, getJoblist, loginfo
import subprocess
from .models import AdditionalInfo

# Get an instance of a logger, log some startup info
logger = logging.getLogger(__name__)
logger.info('%s :: %s :: %s' % ('uploadmedia startup', '-', '-'))


TITLE = 'Bulk Media Uploader'

override_options = [['ifblank', 'Overide only if blank'],
                    ['always', 'Always Overide']]

overrride_default = 'ifblank'


class im:  # empty class for image metadata
    pass

im.BMUoptions = getBMUoptions()

def prepareFiles(request, validateonly, BMUoptions, constants):
    jobnumber = constants['jobnumber']
    jobinfo = {}
    images = []
    for lineno, afile in enumerate(request.FILES.getlist('imagefiles')):
        # print afile
        try:
            print "%s %s: %s %s (%s %s)" % ('id', lineno + 1, 'name', afile.name, 'size', afile.size)
            image = get_exif(afile)
            filename, objectnumber, imagenumber = getNumber(afile.name, INSTITUTION)
            datetimedigitized, dummy = assignValue('', 'ifblank', image, 'DateTimeDigitized', {})
            imageinfo = {'id': lineno, 'name': afile.name, 'size': afile.size,
                         'objectnumber': objectnumber,
                         'imagenumber': imagenumber,
                         # 'objectCSID': objectCSID,
                         'date': datetimedigitized}
            for override in BMUoptions['overrides']:
                dname,refname = assignValue(constants[override[2]][0], constants[override[2]][1], image, override[3], override[4])
                imageinfo[override[2]] = refname
                # add the Displayname just in case...
                imageinfo['%sDisplayname' % override[2]] = dname

            if not validateonly:
                handle_uploaded_file(afile)

            for option in ['handling', 'approvedforweb']:
                if option in request.POST:
                    imageinfo[option] = request.POST[option]
                else:
                    imageinfo[option] = ''

            if 'handling' in request.POST:
                handling = request.POST['handling']
                for parms in BMUoptions['bmuconstants'][handling]:
                    imageinfo[parms] = BMUoptions['bmuconstants'][handling][parms]

                # special case:
                # borndigital media have their mh id numbers unconditionally replaced with a sequence number
                if imageinfo['handling'] == 'borndigital':
                    # for these, we create a media handling number...
                    # options considered were:
                    # DP-2015-10-08-12-16-43-0001 length: 27
                    # DP-201510081216430001 length: 21
                    # DP-2CBE859E990BFB1 length: 18
                    # DP-2cbe859e990bfb1 length: 18 the winner!
                    mhnumber = jobnumber + ("-%0.4d" % (lineno + 1))
                    #mhnumber = hex(int(mhnumber.replace('-','')))[2:]
                    imageinfo['objectnumber'] = 'DP-' + mhnumber
                images.append(imageinfo)

        except:
            raise
            if not validateonly:
                # we still upload the file, anyway...
                handle_uploaded_file(afile)
            images.append({'name': afile.name, 'size': afile.size,
                           'error': 'problem extracting image metadata, not processed'})

    if len(images) > 0:
        jobinfo['jobnumber'] = jobnumber

        if not validateonly:
            writeCsv(getJobfile(jobnumber) + '.step1.csv', images, FIELDS2WRITE)
        jobinfo['estimatedtime'] = '%8.1f' % (len(images) * 10 / 60.0)

        if 'createmedia' in request.POST:
            jobinfo['status'] = 'createmedia'
            if not validateonly:
                loginfo('start', getJobfile(jobnumber), request)
                try:
                    retcode = subprocess.call([path.join(POSTBLOBPATH, 'postblob.sh'), INSTITUTION, getJobfile(jobnumber), BATCHPARAMETERS])
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
    im.validateonly = 'validateonly' in request.POST

    constants = {}

    for override in im.BMUoptions['overrides']:
        if override[2] in request.POST:
            constants[override[2]] = [request.POST[override[2]],request.POST['override%s' % override[2]]]
        else:
            constants[override[2]] = ['', 'never']

    return constants


@csrf_exempt
#@logged_in_or_basicauth()
def rest(request, action):
    elapsedtime = time.time()
    status = 'error' # assume murphy's law applies...

    if request.FILES:
        constants = setConstants(request, im)
        jobinfo, images = prepareFiles(request, im.validateonly, im.BMUoptions, constants)
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
    constants['jobnumber'] = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())

    if request.POST:
        jobinfo, images = prepareFiles(request, im.validateonly, im.BMUoptions, constants)
    else:
        jobinfo = {}
        images = []

    timestamp = time.strftime("%b %d %Y %H:%M:%S", time.localtime())
    elapsedtime = time.time() - elapsedtime
    logger.info('%s :: %s :: %s' % ('uploadmedia job ', constants['jobnumber'], '-'))

    return render(request, 'uploadmedia.html',
                  {'apptitle': TITLE, 'serverinfo': SERVERINFO, 'images': images, 'count': len(images),
                   'constants': constants, 'jobinfo': jobinfo, 'validateonly': im.validateonly,
                   'dropdowns': im.BMUoptions, 'override_options': override_options, 'status': status, 'timestamp': timestamp,
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
    elapsedtime = time.time() - elapsedtime
    status = 'up'
    timestamp = time.strftime("%b %d %Y %H:%M:%S", time.localtime())

    return render(request, 'uploadmedia.html', {'filenames2check': listoffilenames,
                                                'objectnumbers': objectnumbers, 'dropdowns': im.BMUoptions,
                                                'override_options': override_options, 'timestamp': timestamp,
                                                'elapsedtime': '%8.2f' % elapsedtime,
                                                'status': status, 'apptitle': TITLE, 'serverinfo': SERVERINFO})


@login_required()
def showresults(request, filename):
    f = open(getJobfile(filename), "rb")
    response = HttpResponse(FileWrapper(f), content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="%s"' % filename
    return response


@login_required()
def deletejob(request, filename):
    try:
        remove(getJobfile(filename))
        logger.info('%s :: %s' % ('uploadmedia job deleted', filename))

    except:
        logger.info('%s :: %s' % ('uploadmedia tried and failed to delete job', filename))
    #return redirect('../showqueue')
    return showqueue(request)


@login_required()
def showqueue(request):
    elapsedtime = time.time()
    jobs, errors, jobcount, errorcount = getJoblist()
    if 'checkjobs' in request.POST:
        errors = None
    elif 'showerrors' in request.POST:
        jobs = None
    else:
        errors = None
    BMUoptions = getBMUoptions()
    elapsedtime = time.time() - elapsedtime
    status = 'up'
    timestamp = time.strftime("%b %d %Y %H:%M:%S", time.localtime())

    return render(request, 'uploadmedia.html',
                  {'dropdowns': BMUoptions, 'override_options': override_options, 'timestamp': timestamp,
                   'elapsedtime': '%8.2f' % elapsedtime,
                   'status': status, 'apptitle': TITLE, 'serverinfo': SERVERINFO, 'jobs': jobs, 'jobcount': jobcount,
                   'errors': errors, 'errorcount': errorcount})
