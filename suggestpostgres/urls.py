__author__ = 'jblowe'

from django.conf.urls import patterns, url
import views

urlpatterns = patterns('',
                       # ex: /suggestpostgres?q=ASPARAG&elementID=ta.taxon
                       url(r'^', views.postgresrequest, name='postgresrequest'),
                       )