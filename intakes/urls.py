__author__ = 'remillet'
from django.conf.urls import patterns, url
from intakes import views

urlpatterns = patterns('',
                       # ex: /intakes/
                       url(r'^$', views.get_intakes, name='get_intakes'),
                       # ex: /intakes/5/
                       url(r'^(?P<intake_csid>[\w-]+)/$', views.get_intake_detail, name='get_intake_detail'),
                       )