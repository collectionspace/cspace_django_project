from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.contrib.auth import views

admin.autodiscover()

#
# Initialize our web site -things like our AuthN backend need to be initialized.
#
from main import cspace_django_site

cspace_django_site.initialize()

urlpatterns = patterns('',
                       #  Examples:
                       #  url(r'^$', 'cspace_django_site.views.home', name='home'),
                       #  url(r'^cspace_django_site/', include('cspace_django_site.foo.urls')),

                       #  Uncomment the admin/doc line below to enable admin documentation:
                       #  url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

                       url(r'^$', 'landing.views.index', name='index'),
                       # these are django builtin webapps
                       url(r'^admin/', include(admin.site.urls)),
                       url(r'^accounts/login/$', views.login, name='login'),
                       url(r'^accounts/logout/$', 'django.contrib.auth.views.logout', name='logout'),

                       # these are "internal webapps", used by other webapps -- not user-facing
                       url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
                       url(r'^service/', include('service.urls')),
                       url(r'^suggestpostgres/', include('suggestpostgres.urls', namespace='suggestpostgres')),
                       url(r'^suggestsolr/', include('suggestsolr.urls', namespace='suggestsolr')),
                       url(r'^suggest/', include('suggest.urls', namespace='suggest')),
                       url(r'^imageserver/', include('imageserver.urls', namespace='imageserver')),

                       # these are user-facing (i.e. present a UI to the caller)
                       #url(r'^asura/', include('asura.urls', namespace='asura')),
                       url(r'^batchuploadimages/', include('batchuploadimages.urls', namespace='batchuploadimages')),
                       url(r'^imagebrowser/?', include('imagebrowser.urls', namespace='imagebrowser')),
                       url(r'^imaginator/?', include('imaginator.urls', namespace='imaginator')),
                       url(r'^internal/', include('internal.urls', namespace='internal')),
                       url(r'^ireports/', include('ireports.urls', namespace='ireports')),
                       url(r'^landing/?', include('landing.urls', namespace='landing')),
                       url(r'^search/', include('search.urls', namespace='search')),
                       url(r'^simplesearch/', include('simplesearch.urls', namespace='simplesearch')),
                       #url(r'^toolbox/', include('toolbox.urls', namespace='toolbox')),
                       url(r'^uploadmedia/', include('uploadmedia.urls', namespace='uploadmedia')),
                       #url(r'^uploadtricoder/', include('uploadtricoder.urls', namespace='uploadtricoder')),
)
