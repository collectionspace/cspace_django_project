__author__ = 'jblowe'

# suggest functionality for webapps that access solr
#
# does NOT use the Solr4 "suggest" facility.
#
# instead, it uses facet queries.
#
# this module is "plug-compatible" with the psql version
#
# invoke as:
#
# http://localhost:8000/suggest/?q=1-200&elementID=ob.objno1
#
# returns json like:
#
# [{"value": "1-200"}, {"value": "1-20000"}, {"value": "1-200000"}, ...  {"value": "1-200025"}, {"s": "object"}]


from django.http import HttpResponse
from os import path
from common import cspace # we use the config file reading function
from cspace_django_site import settings
from common.appconfig import getParms, loadConfiguration

import solr

searchConfig = cspace.getConfig(path.join(settings.BASE_PARENT_DIR, 'config'), 'suggestsolr')
FIELDEFINITIONS = searchConfig.get('solr', 'FIELDDEFINITIONS')

# read this app's config file
prmz = loadConfiguration('common')
prmz = getParms(path.join(settings.BASE_PARENT_DIR, 'config/' + FIELDEFINITIONS), prmz)

# create a connection to a solr server
s = solr.SolrConnection(url='%s/%s' % (prmz.SOLRSERVER, prmz.SOLRCORE))

import sys, json, re
import cgi
import cgitb

cgitb.enable()  # for troubleshooting


def solrtransaction(q, elementID):

    #elapsedtime = time.time()

    try:

        # do a search
        solrField = prmz.PARMS[elementID][3]
        # just distinguishing the 2 functions of this field:
        # 1. the _s version, suggestfield, is the string field to display
        # 2. the _txt version, searchfield, is the field to search on (i.e. keywords)
        suggestfield = solrField
        # usually we will search using the _txt field, but 'string' and other fields need to use the _s version
        if 'string' in prmz.PARMS[elementID][1] or 'objectno' in prmz.PARMS[elementID][1]:
            searchfield = solrField
        else:
            searchfield = solrField.replace('_ss','_txt')
            searchfield = searchfield.replace('_s','_txt')
        # yes, case is a terrible thing to have to deal with!
        q2 = q.lower().split(' ')
        # make every token a left prefix...
        q3 = [x + '*' for x in q2]
        querystring = searchfield + ':' + (' AND %s:' % searchfield).join(q3)
        #querystring = '%s:%s*' % (searchfield,q)
        print querystring
        response = s.query(querystring, facet='true', facet_field=[ suggestfield ], fq={},
                           rows=0, facet_limit=30,
                           facet_mincount=1)

        facets = response.facet_counts
        facets = facets['facet_fields']
        result = []
        for key, values in facets.items():
            for k, v in values.items():
                missingatoken = filter(lambda x: x not in k.lower(), q2)
                if not missingatoken:
                    result.append(k)

        result.sort(key=lambda v: v.upper())
        result = [ {'value': v} for v in result]
        result.append({'s': solrField})

        # return suggested in alphabetical order (case insensitive)
        return json.dumps(result)

    except:
        raise
        sys.stderr.write("suggest solr query error!\n")
        return None

#@login_required()
def solrrequest(request):
    elementID = request.GET['elementID']
    q = request.GET['q']
    return HttpResponse(solrtransaction(q,elementID), content_type='text/json')


