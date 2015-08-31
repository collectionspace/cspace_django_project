__author__ = 'jblowe'

from django.conf.urls import patterns, url
import views

urlpatterns = patterns('',
                       # ex: /suggest?q=ASPARAG&elementID=family&source=solr
                       url(r'^', views.suggest, name='suggest'),
                       )