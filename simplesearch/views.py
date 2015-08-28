__author__ = 'jblowe'

import re

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

# alas, there are many ways the XML parsing functionality might be installed.
# the following code attempts to find and import the best...
try:
    from xml.etree.ElementTree import tostring, parse, Element, fromstring

    print("running with xml.etree.ElementTree")
except ImportError:
    try:
        from lxml import etree

        print("running with lxml.etree")
    except ImportError:
        try:
            # normal cElementTree install
            import cElementTree as etree

            print("running with cElementTree")
        except ImportError:
            try:
                # normal ElementTree install
                import elementtree.ElementTree as etree

                print("running with ElementTree")
            except ImportError:
                print("Failed to import ElementTree from any known place")

from common import cspace
from cspace_django_site.main import cspace_django_site

config = cspace_django_site.getConfig()
TITLE = 'Simple Keyword Search'


@login_required()
def simplesearch(request):
    if 'kw' in request.GET and request.GET['kw']:
        kw = request.GET['kw']
        # do search
        connection = cspace.connection.create_connection(config, request.user)
        (url, data, statusCode) = connection.make_get_request(
            'cspace-services/%s?kw=%s&wf_deleted=false' % ('collectionobjects', kw))
        # ...collectionobjects?kw=%27orchid%27&wf_deleted=false
        cspaceXML = fromstring(data)
        items = cspaceXML.findall('.//list-item')
        results = []
        for i in items:
            outputrow = []
            csid = i.find('.//csid')
            csid = csid.text
            objectNumber = i.find('.//objectNumber')
            objectNumber = objectNumber.text
            hostname = connection.protocol + ':' + connection.hostname
            if connection.port != '': hostname = hostname + ':' + connection.port
            link = '%s/collectionspace/ui/%s/html/cataloging.html?csid=%s' % (hostname, connection.tenant, csid)
            outputrow.append(link)
            outputrow.append(objectNumber)
            additionalfields = []
            for field in ['objectName', 'title', 'updatedAt']:
                element = i.find('.//%s' % field)
                element = '' if element is None else element.text
                # extract display name if a refname... nb: this pattern might do damage in some cases!
                element = re.sub(r"^.*\)'(.*)'$", "\\1", element)
                additionalfields.append(element)
            outputrow.append(additionalfields)
            results.append(outputrow)
        return render(request, 'simplesearch.html',
                      {'apptitle': TITLE, 'results': results, 'kw': kw,
                       'labels': 'Object Number|Object Name|Title|Updated At'.split('|')})

    else:
        return render(request, 'simplesearch.html', {'apptitle': TITLE})
