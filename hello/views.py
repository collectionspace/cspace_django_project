from django.http import HttpResponse


def home(request):
    return HttpResponse('Hello, world. This is the testapp. click <a href="landing">here</a> to see webapps available.')