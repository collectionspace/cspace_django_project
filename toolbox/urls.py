__author__ = 'jblowe'

from django.conf.urls import patterns, url
from toolbox import views

urlpatterns = patterns('',
                       url(r'^$', views.index, name='index'),
                       url(r'^(?P<appname>[\w\-]+)/?', views.tool, name='toolbox'),
                       )
