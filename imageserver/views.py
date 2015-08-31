__author__ = 'jblowe'

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponse
from common import cspace # we use the config file reading function
from cspace_django_site import settings

from os import path
import urllib2
import time
import logging
import base64

config = cspace.getConfig(path.join(settings.BASE_PARENT_DIR, 'config'), 'imageserver')
username = config.get('connect', 'username')
password = config.get('connect', 'password')
hostname = config.get('connect', 'hostname')
realm = config.get('connect', 'realm')
protocol = config.get('connect', 'protocol')
port = config.get('connect', 'port')
port = ':%s' % port if port else ''


imageunavailable = config.get('connect', 'imageunavailable')

server = protocol + "://" + hostname + port

# Get an instance of a logger, log some startup info
logger = logging.getLogger(__name__)
logger.info('%s :: %s :: %s' % ('imageserver startup', '-', '%s' % server))

#@login_required()
def get_image(request, image):
    try:
        elapsedtime = time.time()

        passman = urllib2.HTTPPasswordMgr()
        passman.add_password(realm, server, username, password)
        authhandler = urllib2.HTTPBasicAuthHandler(passman)
        opener = urllib2.build_opener(authhandler)

        unencoded_credentials = "%s:%s" % (username, password)
        auth_value = 'Basic %s' % base64.b64encode(unencoded_credentials).strip()
        opener.addheaders = [('Authorization', auth_value)]

        urllib2.install_opener(opener)

        url = "%s/cspace-services/%s" % (server, image)
        f = urllib2.urlopen(url)
        data = f.read()
        elapsedtime = time.time() - elapsedtime
    except:
        logger.info('%s :: %s :: %s' % ('image error', '-', '%s :: %8.3f seconds' % (image, elapsedtime)))
        image404 = open(path.join(settings.BASE_PARENT_DIR, 'cspace_django_site/static/cspace_django_site/images', imageunavailable),'r').read()
        return HttpResponse(image404, content_type='image/jpeg')

    logger.info('%s :: %s :: %s' % ('image', '-', '%s :: %8.3f seconds' % (image, elapsedtime)))
    return HttpResponse(data, content_type='image/jpeg')
