__author__ = 'jblowe'

from django.conf.urls import patterns, url
from uploadmedia import views

urlpatterns = patterns('',
                       url(r'^/?$', views.uploadfiles),
                       url(r'^uploadfiles', views.uploadfiles, name='uploadfiles'),
                       url(r'^rest/(?P<action>[\w\-\.]+)$', views.rest, name='rest'),
                       url(r'^checkfilename', views.checkfilename, name='checkfilename'),
                       url(r'^showqueue', views.showqueue, name='showqueue'),
                       url(r'^showresults/(?P<filename>[\w\-\.]+)$', views.showresults, name='showresults'),
                       #url(r'createmedia', views.createmedia, name='createmedia'),
                       )
