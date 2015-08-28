__author__ = 'jblowe'

from django.conf.urls import patterns, url
from django.views.decorators.cache import cache_page
from imageserver import views

urlpatterns = patterns('',
                       # ex: /imageserver/blobs/5dbc3c43-b765-4c10-9d5d/derivatives/Medium/content
                       #url(r'^(?P<image>.+)$', views.get_image, name='get_image'),
                       # cache images for 180 days..
                       url(r'^(?P<image>.+)$', cache_page(60 * 60 * 24 * 180)(views.get_image),name='get_image'),
                       )