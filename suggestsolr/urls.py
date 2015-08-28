__author__ = 'jblowe'

from django.conf.urls import patterns, url
import views

urlpatterns = patterns('',
                       # ex: /suggestsolr?q=ASPARAG&elementID=family
                       url(r'^', views.solrrequest, name='solrrequest'),
                       )