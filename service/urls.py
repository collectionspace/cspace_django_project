__author__ = 'remillet'
from django.conf.urls import patterns, url
from service import views

urlpatterns = patterns('',
                       # ex: /service/intakes
                       url(r'^(?P<service>[\w-]+)/$', views.get_list, name='get_list'),
                       # ex: /service/intakes/a123-b345-456d
                       url(r'^(?P<service>[\w-]+)/(?P<item_csid>[\w-]+)/$', views.get_item, name='get_item'),
                       )