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
from suggestsolr.views import solrrequest
from suggestpostgres.views import postgresrequest

#@login_required()
def suggest(request):
    response = None
    try:
        source = request.GET['source']
        if source == 'solr':
            response = solrrequest(request)
        elif source == 'postgres':
            response = postgresrequest(request)
        else:
            pass
    except:
        pass
    return HttpResponse(response, content_type='text/json')


