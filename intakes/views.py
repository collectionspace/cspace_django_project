__author__ = 'remillet'

from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.http import HttpResponse
from django.http import Http404
from common import cspace
from cspace_django_site.main import cspace_django_site


def handle_request(request, targetUrl):
    """
        This method opens a connection to the configured CollectionSpace services instance and performs
        an authenticated GET request on the targetUrl.  It returns the result from the services to the original
        requester.
    :param request: The incoming request
    :param targetUrl: The URL of the resource to fetch
    :return: :raise:
    """
    config = cspace_django_site.getConfig()
    connection = cspace.connection.create_connection(config, request.user)
    (targetUrl, data, statusCode) = connection.make_get_request(targetUrl)

    if statusCode == 200:
        result = HttpResponse(data, mimetype='application/xml')
    elif statusCode == 404:
        raise Http404
    elif statusCode == 401:
        logout(request)
        result = redirect(cspace.LOGIN_URL_REDIRECT % request.path)
    else:
        result = HttpResponse("HTTP request error: %d." % statusCode)

    return result


@login_required()
def get_intakes(request):
    """
        This method is invoked by the Django framework when it sees the URI "/intakes"

    :param request: The incoming HTTP request
    :return:
    """
    return handle_request(request, 'cspace-services/intakes')


@login_required()
def get_intake_detail(request, intake_csid):
    """
        This method is invoked by the Django framework when it sees the URI "/intakes/{csid}" where {csid} is
        a valid identifier to a CollectionSpace Intake record.

    :param request:
    :param intake_csid:
    :return:
    """
    return handle_request(request, 'cspace-services/intakes/%s' % intake_csid)
