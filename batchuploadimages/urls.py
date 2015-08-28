__author__ = 'jblowe'

from django.conf.urls import patterns, url
from batchuploadimages import views

urlpatterns = patterns('',
                       url(r'^uploadimage/(?P<image>.+)$',views.post_item,name='get_image'),
                       )