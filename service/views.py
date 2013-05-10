__author__ = 'remillet'

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from common import cspace
from cspace_django_site.main import cspace_django_site


@login_required()
def get_list(request, service):
    config = cspace_django_site.getConfig()
    connection = cspace.connection.create_connection(config, request.user)
    (url, data, statusCode) = connection.make_get_request('cspace-services/%s' % service)
    return HttpResponse(data, mimetype='application/xml')

@login_required()
def get_item(request, service, item_csid):
    config = cspace_django_site.getConfig()
    connection = cspace.connection.create_connection(config, request.user)
    (url, data, statusCode) = connection.make_get_request('cspace-services/%s/%s' % (service,item_csid))
    return HttpResponse(data, mimetype='application/xml')
