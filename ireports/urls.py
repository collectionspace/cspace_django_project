__author__ = 'jblowe'

from django.conf.urls import patterns, url
from ireports import views

urlpatterns = patterns('',
                       url(r'^$', views.index, name='index'),
                       url(r'^(?P<report_csid>[\w-]+)/$', views.ireport, name='report'),
                       )
