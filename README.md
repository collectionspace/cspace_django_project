## cspace-django-project

This Django project supports easy access to various CollectionSpace services. To preview
several deployments of this project, visit: https://webapps.cspace.berkeley.edu.

The following components are provided with this project:

#### Core Applications (user-facing apps that you might actually use)

* imagebrowser - a "lightbox-like" app that tiles images based on a keyword query to Solr backend
* imageserver - cacheing proxy server to serve images from CSpace server
* imaginator - "google-lookalike" search app -- provides "N blue links" for a keyword search
* internal - internal (authenticating) search appliance
* search - public (non-authenticating) search appliance
* searchmedia - public (non-authenticating) search appliance for media record
* ireports - interface to installed reports that take inputs other than CSIDs
* uploadmedia - "bulk media uploader" (BMU)

#### Helper Applications (needed by other apps, e.g. search)

* suggest - provides term suggestions (GET request, returns JSON)
* suggestpostgres - provides term suggestions from via Postgres queries
* suggestsolr- provides term suggestions via Solr facet queries
* landing - a "landing page" to ease navigation between apps
* mobileesp - mobile device support; only slightly used so far

#### "Demo" Applications (only to show how this 'framework' works, and to show how to access CSpace)

* hello - simple default app to help you figure out if your Django deployment is working
* service - proxies calls to services; mostly for test purposes

#### Directories (in which you'll need to understand, and/or put stuff in)

* config - put your config files here. This directory is git-ignored
* cspace_django_site - "core" site code -- urls.py, settings.py, etc.
* fixtures - fixtures are used by several apps to provision nav bar and other items
* authn - need by authentication backend. Basically: do not touch
* common - code used across all apps

#### More Obsure Applications (disabled by default, but available)

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
pip install -r pycharm_requirements.txt
# configure Django for your environment. 'pycharm' is the least demanding.
./setup.sh configure pycharm
# deploy a tenant. 'default' points to 'nightly.collectionspace.org'. otherwise, roll your own.
./setup.sh deploy default
# if it all works...
python manage.py runserver
# if the server comes up OK, you should see a landing page in your browser at
http://localhost:8000
# if so, your webapps are pretty much working!
```

### Less Quick Guide: Setting Up for Development or Production

##### Caveats and General Observations

* As illustrated in the Quick Start Guide, the process to deploy this Django project is pretty conventional: get code, resolve system dependencies, configure, and start 'er up. At the moment, the project does not use any of the popular deployment systems out there, e.g. Kubernetes or Docker. Instead, you have to do it by hand, but there are helpers!

* For starters, you'll need to set up Django and install some Python modules (see the various `*_requirements.txt` files)

* The project does run in a variety of different environments.

* Next you'll need to `configure` your project for a particular target environment: `prod`, `dev`, or `pycharm`.  The first two option are of course intended to support running the webapps in either of two server environments; currently, they are suitable for OSX, RedHat, and Ubuntu deployments.  As a developer, you'll probably want to use the `pycharm` target, which is only a little different from the other two: it does not deploy the image caching option, and it turns off Universal Analytics.

* You need to have a CollectionSpace server to point to. Even before you start playing with your own, you should consider deploying the *Sample Deployment*, which points to the development server at `nightly.collectionspace.org`.  This setup is quite easy to get working -- few dependencies, and all the assumptions about configuration are made for you.

* So -- `configuration` is used here to talk about the setup required for different environments, and `deployment` is used to refer setting up the project for the particular CollectSpace tenant (server) you will be using. Got it?

* A helper script called `setup.sh` is provided to help with all this. It is described in some detail below. You should use it, though it is not required. `setup.sh` remembers to perform all the little Django details required when setting up and maintaining the project, but note there may be times when you'll need to go around it, at least in development.

* This project comes with **sample** configuration files that point to the development server at `nightly.collectionspace.org`. These are
located in `config.examples/` and you will need to copy them to the working directory `config/` in order to make the apps work. The files in `config/` are 'git-ignored'. When you start working with a real deployment, you'll need to modify these files to point to your real CollectSpace server, and you'll need to take care of the files yourself. 

* So. To summarize. Almost all webapps require a config file, some require two. Therefore, the `config` will be quite full of config files for the varioius apps. An example configuration file for each webapp is included, but you *will* eventually need to make your own. If the webapp is called `webapp`, the corresponding configuration file should be called `webapp.cfg` unless there is a good reason not to.

##### Recipe for Development Deployments

The following recipe assumes you are deploying in a development environment, on a Mac, RedHat, or Ubuntu system. And that you will use the development server that comes with Django or that you'll be using PyCharm as your IDE (it has a builtin server). If you are deploying in a UCB-managed server environment (i.e. Red Hat), see further below.

First, fork the `cspace-deployment/cspace_django_project` in your own account on GitHub.

Then on your development system, you'll want to clone your development fork of the repo in whatever directory you do your PyCharm development in. For me, I put them all in `~/PyCharmProjects`.

You'll need to install a number of Python modules (see `*_*requirements.txt`).  PyCharm can help you with this, or you can
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
with PyCharm and supports multiple Python interpreters. 

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
# to deploy a specific tetant, you'll want to clone the repo with all the
# example config files out side of this repo, i.e. in ~/django_example_config
cd .. ; git clone https://github.com/cspace-deployment/django_example_project.git
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

#### Ubuntu 14.04+

We assume that you already have CollectionSpace properly installed, configured, and running on your machine. Furthermore, this sections walks you through the steps to setup the CSpace Django Applications as a service on your machine.

##### Step 1: Get the source code

This is pretty self explanatory, although we will manipulate the location of the source code to make our lives a little
 easier when configuring our web server and enabling our site. 

```bash
# Switch to the root user, being careful and mindful of your actions from here on out
$ sudo su -

# Navigate to the local shared directory
cd /usr/local/share/

# Create a new directory to store your code 
mkdir -p django/webapp

# Jump to that directory
cd django/webapp/

# Clone the code from the remote GitHub repository 
git clone https://github.com/cspace-deployment/cspace_django_project.git

# Note: if you don't have git
apt-get install git

# Copy source code to the parent directory while within the parent directory ...
# ... this isn't entirely necessary, but it helps to keep the default url path neat.
# You'll see why later, when configuring your Apache2 server.  
cp -r cspace_django_project/* .

# Remove the old directory
rm -r cspace_django_project
```


##### Step 2: Get the Apache2 Web Server

This is one of the most common web servers for Linux systems, and is used to serve webpages to the client machine, i.e. a web server. You can read more about it here: https://httpd.apache.org/.

If you already have Apache2 installed, you can skip this step.

```bash
# Use the Advanced Packaging Tool (apt) to update your system packages
apt-get update

# Use 'apt' to install Apache2, effectively installing it in the directory...
# ... /etc/apache2
apt-get install apache2

# Check that Apache2 is running
service apache2 status

# If not, start up your new Apache2 Web Server
service apache2 start
```

##### Step 3: Get Python related packages and set up your Virtual Environment

We will install and designate a Virtual Environment for our CSpace Django Application in order to separate
its dependencies from other current or future Django applications. For now, we will just install them. 

```bash
# As root user, check your Python version, you'll need 2.7 not 3+
python -V

# Check your 'Pip Installs Packages' Python package manager (pip) version
# It should be the latest if you updated your system packages as done earlier here
pip -V

# Use Ubuntu's package manger to install the following Python packages to deal with PyGreSQL errors you're likely...
# ... to encouter with out them
apt-get install python-dev
apt-get install python-psycopg2


apt-get install libpq-dev

# Now, install virtualenvironemnt
pip install virtualenv

# Navigate to the source code directory, or /usr/local/share/django/webapp/
# Create a dedicated virtual environment ('cspace_venv' in this case, but feel free to name it whatever you want)
virtualenv cspace_venv

# Activate your new virtual environment
source cspace_venv/bin/active

# Now, install the application dependencies, from within your new virtual environment
# This should work, however, if you happen to get any errors, it's likely due to the lack of some system wide Python...
# dependencies. Therefore, a simple search of the error should provide a solution, or multiple
pip install -r pycharm_requirements.txt
```

##### Step 4: Get the Apache mod_wsgi Django module

This module is used to host Python WSGI applications on your Apache2 Web Server. You can inquire more about this module
by navigating to: https://docs.djangoproject.com/en/1.9/howto/deployment/wsgi/modwsgi/

```bash
# Install the Apache mod_wsgi module
apt-get install libapache2-mod-wsgi
```

##### Step 5: Configuring the CSpace Django Web Application

As mentioned earlier, in several places, you'll need to provide your own configurations files prior to deployment.
Lucky for you, many default examples have been provided in the 'config.examples' directory. Hence, we will need to copy
them over to our 'config' directory prior to running the 'setup.sh' script. 

```bash
# While still, as the root user, within our dedicated virtual environment the (cspace_venv), and the 'webapp' directory
# Copy over the provided configuration files
cp -r config.examples/*.cfg config

# Use the provided 'setup.sh' script to configure
./setup.sh configure pycharm

# And, to deploy
# Ignore the warnings for now, however, not errors if you happen to experience any
./setup.sh deploy default
```

##### Step 6: Edit the wsgi.py script

We will need to let our Apache2 web server know where to find the dependencies we've dedicated for our CSpace Django
Application, within our virtual environment. Uncomment the following lines from the wsgi.py script found in the 
'webapp/cspace_django_site' directory. 

```bash
1 # import site
.
.
.
14 # activate_env = os.path.expanduser('/usr/local/share/django/webapp/cspace_venv/bin/activate_this.py')
15 # execfile(activate_env, dict(__file__=activate_env))
.
.
.
31 # from django.core.wsgi import get_wsgi_application
32 # application = get_wsgi_application()
```

And, comment out the line...

```bash
28 application = django.core.handlers.wsgi.WSGIHandler()
```

##### Step 7: Configure the Apache2 Web Server

Necessary in order to allow the web server to talk to our CSpace Django Application, copy the 000-default-Ubuntu-VE.conf found in the 'webapp/config.examples' directory to the Apache2 'site-enabled' directory. 

```bash
# Still, as the root user, from within the config.examples directory
cp ./000-default-Ubuntu-VE.conf /etc/apache2/site-enabled/

# Rename the default Apache2 conf file, just to have
# From within the '/etc/apache2/site-enabled/' directory
mv 000-default.conf 000-default-OLD.conf

# Then, rename the Ubuntu-VE conf file to replace Apache2's default
mv 000-default-Ubuntu-VE.conf 000-default.conf
```

##### Step 8: Collect the static files

We will need to collect all of the static files for our CSpace Django Application. Otherwise, if you restart the Apache2 server now, everything will be in plain HTML.

```bash
# From within the webapp directory, and our activate virtual environment ('cspace_venv')
# Type 'yes' when prompted
python manage.py collectstatic
```

##### Step 9: Restart Apache2

We should be all set, all that remains for deployment is to restart the Apache2 web server. 

```bash
# restart the Apache2 web server
service apache2 restart
```

That should do it. Go ahead and navigate to http://your_ip_address/webapp in your browser to check if the CSpace Django Application was deployed successfully. 

##### Troubleshooting

If you happen to run into errors, the Apache2 server log is a great place to start. This can be found in the 'var/logs/apache2/' directory.  

```bash
# As the root user
tail -f /var/logs/apache2/error.log
```

Note: It's quite possible that you'll need to change the permissions on the Apache2 log directory so that the web server can write to the error log, among others.

You may also need to disable some of the pre-installed web apps, as described at the beginning of this document. 

```bash
# Again, form within the webapp directory, and the virutal environment
# To show all of the currently installed web apps
./setup show

# And, to disable any web apps giving you errors, likely due to configurations that still need to be completed
./setup disable [app]
```

In addition, the Django logs can be found in the 'webapp/logs' directory.

```bash
# From within the 'webapp/logs' directory
tail -f logfile.txt
```

##### Step 10: Connecting to your PostgreSQL database

Hopefully by now you have an instance of the CSpace Django Application running at http://your_ip_address/webapp. If not, feel free to post a question on the CollectionSpace Talk list, found here: http://lists.collectionspace.org/mailman/listinfo/talk_lists.collectionspace.org

Continuing on, we will need to connect to your PostgreSQL database by editing various provided configuration files.

Within the settings.py module, found at 'webapp/cspace_django_site/', update the following lines with your PostgreSQL credentials. 

```bash
29 DATABASES = {
30     'default': {
31         'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3    ' or 'oracle'.
32         'NAME': '<your_database_name>', # BASE_PARENT_DIR + os.sep + 'db.sqlite3',  # Or path todatabase file     if using sqlite3.
33         # The following settings are not used with sqlite3:
34         'USER': '<your_database_user>',
35         'PASSWORD': '<your_databse_password>',
36         'HOST': '', # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
37         'PORT': '<your_postgres_connection_port>', # Set to empty string for default (5432)
38     }
39 }
```

Next, jump back out to the 'webapp' directory and run:

```bash
# As root user, and within our activated virtual environment ('cspace_venv')
python manage.py syncdb
```

##### Step 11: Install and Setup Apache Solr

A free, open source, blazing fast, and highly popular enterprise search platform written in Java. We suggest you familiarize yourself with the Solr documentation, as it will come in handy later when extending your CSpace Django Web Applications. You can read more about Apache Solr, here: http://lucene.apache.org/solr/resources.html#documentation.

Also, you'll see later how we use Solr with the default public search application, but for now feel free to take a look at the fields definition file found here: https://wiki.collectionspace.org/pages/viewpage.action?pageId=158302621

```bash
# Still, as the root user, navigate to the solr directory
cd /usr/local/share/django/webapp/solr

# Use the provided script to install Solr with multiple cores for your tenant
# Calls with four arguments: fullpathtosolr4dir solrversion topnode tenants
# topnode is the directory with fullpathtosolr4dir in which the data and 
# configuration for all solr tenants goes
# List of 1 or more tenants as a quoted string, e.g. "pahma botgarden ucjeps",
# this will create 3 cores for each tenant, x-public, x-internal, x-media
./configureMultiCoreSolr.sh /usr/local/share/solr4 4.10.4 topnode "your_tenants"
```

You should see something like this:

```bash
"Waiting up to 30 seconds to see Solr running on port 8983[/]
Started Solr server on port 8983 (pid=10310). Happy searching!

Found 1 Solr nodes: ...
"
```

There is another script developed to help with calling your Solr server, solrserver.sh. You may need to configure this properly so that it points to your Solr server, either editing the script or adding it as environmental variable, i.e. SOLRDIR="/usr/local/share/solr4/xxx



##### Step 12: Indexing Apache Solr 

There is so much more to understand regarding Solr, its configuration files, and UCB developed scripts. We won't go into 
a lot of detail here, but you can learn more from reading the README.md located in the 'webapp/solr/' directory.
For now, let's just get set up. 

Navigate to the 'webapp/solr' directory and edit the 'set-tenant-default' script with your database connection information.
 
```bash
# Still, as the root user, edit the following lines with your information
10   export SERVER="localhost port=5432 sslmode=prefer" # Typical default settings, changes if needed
11   export USERNAME="<user_name>"
12   export DATABASE="<database_name>"
13   # note that the password is not here. best practice is to
14   # store it in .pgpass. 
15   # if you need to set it here, add it to the CONNECT_STRING
16   export CONNECTSTRING="host=$SERVER password='<database_user_password>' dbname=$DATABASE"
```

Once that is completed, rename the following PostgreSQL scripts using your tenant name.

```bash
# as the root user, and within the 'webapp/solr' directory
mv core.public.sql <your_tenant_name>.public.sql
mv core.internal.sql <your_tenant_name>.internal.sql
```

Next, in addition to some edits, do the same with the field definition files, found in the 'webapp/config' directory.

```bash
# as the root user, and within the 'webapp/config' directory
mv corepublicparms.csv <your_tenant_name>publicparms.csv
mv coreinternalparms.csv <your_tenant_name>internalparms.csv
```

Now, open up both files and edit line #14 to match the name of your tenant. 

For example, for the <your_tenant_name>publicparms.csv file:

```bash
     # From
14   core core-public 
     # To
14   <your_tenant_name><your_tenant_name>-public
```

While we're here, within the 'webapp/config' directory, we will need to edit some configuration files to reflect the changes that we just made. 

In the 'common.cfg' file:

```bash
12 # the following is used to construct URLs that link this app to a CSpace server
13 CSPACESERVER        = http://<your_cspace_ip_address>:8180/
14 INSTITUTION         = <institution_name>
.
.
17 IMAGESERVER        = http://<your_cspace_ip_address>/webapp/imageserver
.
.
.
32 # csv filename construction parameters
33 CSVPREFIX           = <your_tenant_id>
34 CSVEXTENSION        = csv
```

In the 'search.cfg' file:

```bash
3 FIELDDEFINITIONS    = <your_tenant_name>publicparms.csv
```

In the 'suggestsolr.cfg' file:

```bash
3 FIELDDEFINITIONS    = <your_tenant_name>publicparms.csv
```

In the 'imageserver.cfg' file:

```bash
1 [connect]
2 protocol          = http
3 port              = 8180
4 realm             = org.collectionspace.services
5 hostname          = <your_cspace_ip>
6 username          = <a_dedicated_user_with_cspace_access>
7 password          = <password>
```

Excellent. Now that we have that out of the way, we can go ahead and jump back into the 'webapp/solr' directory. Here we will use the provided script effectively index Solr. What do this mean exactly? In brief, when we index Solr, we are querying the CollectionSpace tenant database using the recently renamed PostgreSQL script, populating a csv file (defined by our fields definitions file and a provided CSpace Solr schema), and pushing it the Solr server. Which, in effect, is where the CSpace Django Application pulls its data. Got it? Good.

Again, you can learn more by checking out the dedicated readme in the 'webapp/solr' directory.

Moving on, go ahead and execute the following in sequence. 

```bash
# from within the webapp/solr/ directory
source set-tenant-default.sh <your_tenant_name>

nohup ./solrETL-template.sh
```

From here, navigate to http://your_ip_address:8983/solr/#/<your_tenant_id>-public/query and hit 'search.' You should see a mass of data in JSON format that was effectively indexed. If not, review the file 'nohup.out' for any errors that may have occurred during the indexing.
 
Finally, restart the Apache2 web server for good measure (usually only needed when making changes to UI components and configurations). 

```bash
# as root user
service apache2 restart
```

Navigate to the application landing page in your browser, and then the public search application. Likely located at 'http:your_ip_address/webapp/search/search' and execute a keyword search using an asterisk as the parameter. If all went well, you should see populated search results containing indexed data from your CollectionSpace tenant database complete with images. 
 
Congratulations! You've effectively deployed your very own UCB CSpace Django Application. 


#### RHEL
###### Coming soon...

For now, you can supplement what has been provided above, for Ubuntu, with general tools and managers that are specific 
to your Linux distribution.

#### Configuring your Django App
##### Coming soon...

For now, please see the CollectionSpace Wiki on how to configure the field definitions file used for the Search portal (https://wiki.collectionspace.org/pages/viewpage.action?pageId=158302621), as well as the Wiki for UC Berkeley web applications: https://wiki.collectionspace.org/display/deploy/UC+Berkeley+web+applications
 
##### Search Portal

##### Image Browser

##### Inventorinator


#### Troubleshooting your Django App within a production environment
