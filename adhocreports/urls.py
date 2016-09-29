__author__ = 'amywieliczka, jblowe'

from django.conf.urls import patterns, url
from adhocreports import views

urlpatterns = patterns('',
                       url(r'^/?$', views.direct, name='direct'),
                       url(r'^search/$', views.search, name='search'),
                       url(r'^search/(?P<fieldfile>[\w-]+)$', views.loadNewFields, name='loadNewFields'),
                       url(r'^results/$', views.retrieveResults, name='retrieveResults'),
                       url(r'^bmapper/$', views.bmapper, name='bmapper'),
                       url(r'^statistics/$', views.statistics, name='statistics'),
                       url(r'^dispatch/$', views.dispatch, name='dispatch'),
                       #url(r'^csv/$', views.csv, name='csv'),
                       #url(r'^pdf/$', views.pdf, name='pdf'),
                       url(r'^gmapper/$', views.gmapper, name='gmapper'),
                       )
