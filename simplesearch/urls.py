__author__ = 'jblowe'

from django.conf.urls import patterns, url
from simplesearch import views

urlpatterns = patterns('',
                       url(r'^$', views.simplesearch, name='index'),
                       )
