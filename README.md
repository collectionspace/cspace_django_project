## cspace-django-project

This Django project supports easy access to various CollectionSpace services.

The following components are provided:

#### Core apps (user-facing apps that you might actually use)

* imagebrowser - a "lightbox-like" app that tiles images based on a keyword query to Solr backend
* imageserver - cacheing proxy server to serve images from CSpace server
* imaginator - "google-lookalike" search app -- provides "N blue links" for a keyword search
* internal - internal (authenticating) search appliance
* search - public (non-authenticating) search appliance
* searchmedia - public (non-authenticating) search appliance for media record
* ireports - interface to installed reports that take inputs other than CSIDs
* uploadmedia - "bulk media uploader" (BMU)

#### Helper Apps (needed by other apps, e.g. search)

* suggest - provides term suggestions (GET request, returns JSON)
* suggestpostgres - provides term suggestions from via Postgres queries
* suggestsolr- provides term suggestions via Solr facet queries
* landing - a "landing page" to ease navigation between apps
* mobileesp - mobile device support; only slightly used so far

#### "Demo" Apps (only to show how this 'framework' works, and to show how to access cspace)

* hello - simple app to help you figure out if your Django deployment is working
* service - proxies calls to services; mostly for test purposes

#### Not apps but directories you'll need to understand and or put stuff in

* config - put your config files here. This directory is git-ignored
* cspace_django_site - "core" site code -- urls.py, settings.py, etc.
* fixtures - fixtures are used by several apps to provision nav bar and other items
* authn - need by authentication backend. Basically: do not touch
* common - code used across apps

#### More obsure apps (disabled by default, but available)

* simplesearch - make query (kw=) to collectionobjects service
* batchuploadimages -- RESTful interface to upload images in bulk

### Quick Start Guide

The following dialog makes a number of assumptions -- that your system is already more-or-less setup for Python and Postgres development; that your existing codebase is recent enough (see version requirements below), etc. 

```bash
# get the code. This is the bleeding edge development repo.
git clone https://github.com/cspace-deployment/cspace_django_project
cd cspace_django_project
# resolve the Python module requirements.
# you'll need to have the PostgreSQL client code as well as the Python setuptools installed...
# on a Mac *most* of this is in XCode Tools... consider 'sudo pip' if you know what you are doing
# other code managers such as homebrew can help with this too.
pip install -r pycharm__requirements.txt
# configure Django for your environment. 'pycharm' is the least demanding.
./setup.sh configure pycharm
# deploy a tenant. 'default' points to 'nightly.collectionspace.org'. otherwise, roll your own.
./setup deploy default
# if it all works...
python manage.py runserver
# if the server comes up OK, you should see a landing page in your browser at
http://localhost:8000
# if so, your webapps are pretty much working!
```

### Less Quick Guide: Setting Up for Development and Other Environments

##### Caveats and General Observations

* As illustrated in the Quick Start Guide, the process to deploy this Django project is pretty conventional: get code, resolve system dependencies, configure, and start 'er up. At the moment, the project does not use any of the popular deployment systems out there, e.g. Kubernetes or Docker. Instead, you have to do it by hand, but there are helpers!

* To start with, need to set up Django and install some Python modules (see the various `*_requirements.txt` files)

* The project does run in a variety of different environments, 


* Next you'll need to `configure` your project for a particular target environment: `prod`, `dev`, or `pycharm`.  The first two option are of course intended to support running the webapps in either of two server environments; currently, they are suitable for OSX, RedHat, and Ubuntu deployments.  As a developer, you'll probably want to use the `pycharm` target, which is only a little different from the other two: it doesn't deploy the image cacheing option, and it turns off Universal Analytics.

* You need to have a CollectionSpace server to point to. Even before you start playing with your own, you should consider deploying the *Sample Deployment*, which points to the development server at `nightly.collectionspace.org`.  This setup is quite easy to get working -- few dependencies, and all the assumptions about configuration are made for you.

* So -- `configuration` is used here to talk about the setup required for different environments, and `deployment` is used to refer setting up the project for the particular CollectSpace tenant (server) you will be using. Got it?

* A helper script called `setup.sh` is provided to help with all this. It is described in some detail below. You should use it, though it is not required. `setup.sh` remembers to perform all the little Django details required when setting up and maintaining the project, but note there may be times when you'll need to go around it, at least in development.

* This project comes with **sample** configuration files that point to the development server at `nightly.collectionspace.org`. These are
located in `config.examples/` and you will need to copy them to the working directory `config/` in order to make the apps work. The files in `config/` are 'git-ignored'. When you start working with a real deployment, you'll need to modify these files to point to your real CollectSpace server, and you'll need to take care of the files yourself. 

* So. To summarize. Almost all webapps require a config file, some require two. Therefore, the `config` will be quite full of config files for the varioius apps. An example configuration file for each webapp is included, but you *will* eventually need to make your own. If the webapp is called `webapp`, the corresponding configuration file should be called `webapp.cfg` unless there is a good reason not to.

##### Recipe for Development deployments

The following recipe assumes you are deploying in a development environment, on a Mac, RedHat, or Ubuntu system. And that you will use the development server that comes with Django or that you'll be using PyCharm as your IDE (it has a builtin server). If you are deploying in a UCB-managed server environment (i.e. Red Hat), see further below.

First, fork the `cspace-deployment/cspace_django_project` in your own account on GitHub.

Then on your development system, you'll want to clone your development fork of the repo in whatever directory you do your PyCharm development in. For me, I put them all in `~/PyCharmProjects`.

You'll need to install a number of Python modules (see `*__*requirements.txt`).  PyCharm can help you with this, or you can
do something like the following:

Note: Before running `pip install -r pycharm_requirements.txt`, make sure that you have PostgreSQL, as well as the Python setuptools package installed, otherwise there will be errors. 

```bash
# clone your fork of the github repo to wherever you want to deploy the webapps
cd ~/PycharmProjects
git clone https://github.com/<mygithubid>/cspace_django_project.git my_test_project
cd my_test_project/
# resolve the Python requirements
pip install -r pycharm_requirements.txt
```

NB: if you intend to use your "native python" you may need to resolve the requirements at the root level, e.g.

```bash
sudo pip install -r pycharm_requirements.txt
```

NB: Yes, you can, and indeed may have to, run your apps in a virtual environment if you are unable or unwilling to use the system defaults. This is covered below.  Also note that PyCharm can help you resolve module dependencies -- `venv` comes pretty much builtin
with PyCharm and supports multiple Python interpreters. However, this document doesn't cover how to do that, please RTFM.

(At the moment, there are few version constraints for this project: Python 2.6.8+ and Django 1.5+; requirements.txt
specifies Django 1.5 or higher, but minor code changes seem to be required to run with Django > 1.8. This project has not been tried with Python 3.)

You are now ready to configure your environment and deploy your tenant-specific parameters. 

##### Using setup.sh

There is no `make` or `mvn` build process for Django webapps, and the deployment process consists of place the code where it can be executed and customizing the parameters used for your particular case (which means editing configuration files by hand).

Instead there is a shell script called `setup.sh` which does the few steps required to make your webapps go.

```bash
# OPTION 1: sample deployment to see if you can get the project to run.
# configure your dev deployment
./setup.sh configure pycharm
# to setup the sample tenant configuration...
./setup.sh deploy default
# now you can start the development server
python manage.py runserver
# remember to ^C to stop the server
```

If you are working on one of the UCB tenants, you'll want to get the configuration files for that tenants. There are 
example configurations for all UCB tenants in a separate GitHub repo. If you clone this repo in your home directory, 
`setup.sh` will do the work of copying all the config files to the right place and initializing the Django project 
to run them.

```bash
# OPTION 2: deploy one of the UCB configurations
# to deploy a specific tentant, you'll want to clone the repo with all the
# example config files out side of this repo, i.e. in ~/django_example_config
cd .. ; git clone https://github.com/cspace-deployment/django_exmmple_project.git 
cd ~/PycharmProjects/my_test_project
./setup.sh deploy ucjeps
# this will blow away whatever tenant was deployed previously and setup the UCJEPS tenant.
# now do the initial Django magic to initialize the project (configure options are: prod, dev, pycharm)
```

**NB: `setup.sh` expect this repo, with this name, to be in your home directory!**

**NB: While most of the parameters for tenants are set up for Production, not all are. At any rate, you will need to make sure that the configuration files in `config` are correct.**

As noted above you can disable any apps that you are not interested in. For example, if your collection does not have images
you will not be interested in any of the webapps named image*. It is a simple matter to disable these, and you can
(re-)enable any time if you like. The process is illustrated below. If you don't, they will appear in the landing page
and you will need to configure them even if they won't really do anything.

```bash
# optional: disable any apps you don't want. the following apps only work if you have a solr datastore configured.
./setup.sh disable imageserver
./setup.sh disable imagebrowser
./setup.sh disable imaginator
```

To enable a disabled webapp do the following and restart the webserver you are using:

```bash
./setup.sh enable uploadmedia
```

NB: this will show *all* apps, including the various helper apps, Django admin apps, etc.

(all the enable/disable functionality does is to comment out these webapps in urls.py and settings.py; you could just
do it yourself by hand.)

To see which apps are enabled:

```bash
./setup.sh show
```

##### Configuration files

Most webapps have an associated configuration file (with extension .cfg). The `search` apps also require a "field
definitions file" which describes all the fields used in search and display and this file is a carefully constructed
.csv file (tabs, no encapsulation).  All of these files need to be placed in the config/ directory and edited to point
to the target CSpace server. Lots of other defaults are set in these files as well. The files are in a (YAML-like) format that is consumed by the Python `ConfigParser' module.

E.g.

```YAML
[info]
logo              = https://nightly.collectionspace.org/collectionspace/ui/core/images/header-logo.png

[imaginator]
#
FIELDDEFINITIONS    = corepublicparms.csv
MAXRESULTS          = 100
TITLE               = Imaginator
```

You should make a version of each of the config files that you'll need, with values appropriate to your specif deployment and tenant.

The sample config files point to `nightly.collectionspace.org. These provide some
limited functionality: `simplesearch` works, as does the single brain-damaged `iReport`. The `service` webapp works, but note it has
no config file: it accesses the server defined in the project's configuration for authentication in `main.cfg`.

### Starting and Stopping Servers

You have deployed the code from GitHub to the directory it will be executed in (or, you've cloned or forked this repo
on your local machine).

You have done the initial configuration with `setup.sh`.

You have `configured` your project and `deployed` your tenant-specific customizations.

Now you start a server...

##### Starting Django's built-in development server

From the command line, while in the project directory, type:

```bash
$ python manage.py runserver
```

and you should see:

```bash
Performing system checks...
System check identified 1 issue (0 silenced).
February 28, 2016 - 20:47:14
Django version 1.7, using settings 'cspace_django_site.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

##### Pycharm Debugger

In PyCharm, you'll need to do a bit of configuration before the project will run:

1. Enable Django Support

```
PyCharm > Preferences > Django
click: Enable Django Support
```

In the dialog window, ensure the following parameters show:

```
Django Project Root: /Users/jblowe/PyCharmProjects/cdp/cspace_django_site
Settings: settings.py
Manage script: /Users/jblowe/PyCharmProjects/cdp/cspace_django_site
```

2. Edit a "Run Configuraiton"

```
Run > Edit Configurations
```

In the dialog window,

```
Expand Defaults (by clicking on the little triangle)
Select: Django Server
Click + (to add a configuration)
Give your configuration a name, e.g. “cspace_django_project”
```

Environment variables: 

```
DJANGO_SETTINGS_MODULE: cspace_django_site.settings
```

... and you will need to ensure that the Python interpreter being used is the right one -- the one that has all your requirements resolved.

Or you can resolve them in PyCharm, but you'll need to RTFM for that.

Now start the debugger! (click on the little ladybug in the upper right)

##### Your Project is Running!

Visit the base URL (locahost:8000 in both PyCharm and default dev server, who knows what in other environments!)

You will be rewarded with a landing page. Or more likely, you will have failed to meet all the setup conditions:

* The BMU and imageserver need to have directories created and accessible to work.
* The needed config files better exist and have all the parms specified that are needed for the app.
* The additional module requirements (e.g. psycopg2 for Postgres) need to be met.

### Development and Production Deployments in Linux Environments

This is covered in another README.
