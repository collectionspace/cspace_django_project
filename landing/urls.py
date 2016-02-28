__author__ = 'jblowe'

from django.conf.urls import patterns, url
from landing import views

urlpatterns = patterns('',
                       url(r'^$', views.index, name='index'),
                       url(r'^applist/?', views.applist, name='applist'),
                       )
