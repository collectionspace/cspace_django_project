cspace-django-project
=====================

This Django project supports easy access to various CollectionSpace services.

The following components are provided:

Core apps (that you might actually use)
=======================================

* imagebrowser - tiles images based on a keyword query to Solr backend
* imageserver - proxy server to serve images from CSpace server
* imaginator - "google-lookalike" search app -- provides "N blue links" for a keyword search
* internal - internal (authenticating) search appliance
* search - public (non-authenticating) search appliance
* ireports - interface to installed reports that take inputs other than CSIDs
* uploadmedia - "bulk media uploader" (BMU)
* batchuploadimages -- RESTful interface to upload images in bulk

Helper Apps (needed by other apps, e.g. search)
===============================================

* suggest - provides term suggestions (GET request, returns JSON)
* suggestpostgres - provides term suggestions from via Postgres queries
* suggestsolr- provides term suggestions via Solr facet queries
* landing - a "landing page" to ease navigation between apps
* mobileesp - mobile device support; only slightly used so far


"Demo" Apps (only to show how this 'framework' works, and to show how to access cspace)
=======================================================================================
* hello - simple app to help you figure out if your Django deployment is working
* service - proxies calls to services; mostly for test purposes
* simplesearch - make query (kw=) to collectionobjects service

Not apps but directories you'll need to understand and or put stuff in
======================================================================

* config - put your config files here. This directory is git-ignored.
* cspace_django_site - "core" site code -- urls.py, settings.py, etc.
* fixtures - fixtures are used by several apps to provision nav bar and other items
* authn - need by authentication backend. Basically: do not touch.
* common - code used across apps.


Some things to note when deploying this project:

* This project comes with configuration files that point to the Demo server at nightly.collectionspace.org. These are
located in config.examples/ and you will need to copy them to config/ in order to make the apps work. Of course,
you'll want to edit to work with your CSpace deployment.

* Most webapps require a config file, and an example configuration file, is included in the app's directory.
Each of these needs to be copied to the *project configuration directory* (config/)
with the file name expected by the webapp (usually "webapp.cfg" where "webapp" is the
directory name of the webapp) and then edited to specific deployment-specific parameters.

* Every Django app needs some initialization: the models, etc. need to get created. To ease this process, there is a 
script setup.sh that does most of what is needed. It is described below. There is a more elablorare set of installation
and update scripts which deploy these "cspace_django_project"-type projects in UCB's RHEL
environments. These may be found in the Tools/deployandrelease repo. In particular, this repo contains scripts to
create and populate a Solr4 muticore datastore, which is needed for the search apps to work.

How to get going...
===================

First, make a clone or a fork of collectionspace/cspace_django_project in the directory in which you intend to run
the project. On RHEL this is probably going to be in /var/www. Depending on details, you will want to configure WSGI
under Apache. You may wish to make a virtual host.

On a development system (i.e. using PyCharm), you'll want to checkout out your development fork / clone of the repo in
whatever directory you do your PyCharm development in. For me, I put them all in ~/PyCharmProjects.

You'll need to install a number of Python modules (see requirements.txt).  PyCharm can help you with this, or you can
do something like the following:

Note: Before running `pip install -r requirements.txt`, make sure that you have PostgreSQL, as well as the Python setuptools package installed, otherwise there will be errors. 

```bash
cd my_cspace_django_project
pip install -r requirements.txt
```

(At the moment, there are few version requirements for this project: Python 2.6.8+ and Django 1.5+; requirements.txt
specifies Django 1.7, but you can downgrade it if you like. This project has not been tried with Python 3.)

You'll need to tell Django which type of deployment to make (prod, dev, or pycharm are currently supported).
This configuration will setup up caching (if needed), run the Django management tasks to get thing started.

The example configuration files in config.examples/ can be copied to config/ to get things started.

If you do not want to run certain webapps you can disable them. For example, if your collection does not have images
you will not be interested in any of the webapps named image*. It is a simple matter to disable these, and you can
(re-)enable any time if you like. The process is illustrated below. If you don't, they will appear in the landing page
and you will need to configure them even if they won't really do anything.


Using setup.sh
==============

```bash
# clone the github repo to wherever you want to deploy the webapps
git clone https://github.com/collectionspace/cspace_django_project.git my_test_project
cd my_test_project/
# deploy the specific tenant's configuration, or the example configuration
# OPTION 1: deploy the included files, which point at nightly.collectionspace.org:
# copy the config files (.cfg and .csv)
cp config.examples/* config
# move the config file used for authentication to the site directory
mv config/main.cfg cspace_django_site
# OPTION 2: deploy one of the UCB configurations
# to deploy a specific tentant, you'll want to clone the repo with all the
# example config files out side of this repo, i.e. in ../django_example_config
# e.g. cd .. ; git clone https://github.com/cspace-deployment/django_exmmple_project.git ; cd my_test_project
./setup deploy ucjeps
# now do the initial Django magic to initialize the project (configure options are: prod, dev, pycharm)
./setup.sh configure pycharm
# optional: disable any apps you don't want
./setup.sh disable imageserver
./setup.sh disable imagebrowser
./setup.sh disable imaginator
./setup.sh disable uploadmedia
# now you can start the development, in pycharm, or restarting Apache, or here on the command line
python manage.py runserver
```
to enable a disabled webapp:

```bash
./setup.sh enable uploadmedia
```

(all the enable/disable functionality does is to comment out these webapps in urls.py and settings.py; you could just
do it yourself by hand.)

The easiest thing to do is to start by disabling (almost) everything, getting the project working, then re-enabling and 
configuring apps that you need one by one.  Perhaps we should distribute this project with (almost) everything
disabled, and have people enable the ones that want?

Most webapps have an associated configuration file (with extension .cfg). The search apps also require a "field
definitions file" which describes all the fields used in search and display and this file is a carefully constructed
.csv file (tabs, no encapsulation).  All of these files need to be placed in the config/ directory and edited to point
to the target CSpace server. Lots of other defaults are set in these files as well.

At this time, all the config files are specific to various UCB deployments, and none of them are included in this repo.
To get an idea of what each one should look like. Visit https://github.com/cspace-deployment/django_example_config

You should make a version of each of the config files that you'll need, with values appropriate to your deployment.

There is a set of config files for some of the webapps that points to demo.collectionspace.org. These provide some
limited functionality: simplesearch works, as does the single brain-damaged iReport. the service webapp works, but has
no config file: it accesses the server defined in the project's configuration for authentication in main.cfg.

OK!
===

You have deployed the code from GitHub to the directory it will be executed in (or, you've cloned or forked this repo
on your local machine).

You have done the initial configuration with setup.sh.

You have created a set of config files for the webapps you want to use in config/ either by typing them all in or
getting them from GitHub.

Now you start a server (in PyCharm, start the debugger or dev server; on Linux, restart Apache -- you did create
a virtual host or otherwise make it possible for Apache to execute the files via WSGI, didn't you?)

Visit the base URL (locahost:8000 in PyCharm, who knows what in other environments!)

You will be rewarded with a landing page. Or more likely, you will have failed to meet all the setup conditions:

* The BMU and imageserver need to have directories created and accessible to work.
* The needed config files better exist and have all the parms specified that are needed for the app.
* The additional module requirements (e.g. psycopg2 for Postgres) need to be met.

