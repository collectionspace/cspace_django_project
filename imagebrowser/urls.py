__author__ = 'jblowe'

from django.conf.urls import patterns, url
from imagebrowser import views

urlpatterns = patterns('',
                       url(r'^$', views.images, name='images'),
                       url(r'^(?P<count>[\d]+)/$', views.images, name='images'),
                       )