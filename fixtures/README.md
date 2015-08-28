The fixtures used for this project contain the content shown in the various "nav bar" items of the various apps.

Each app has 0 or more items; these can be managed (edited and organized) using the Django admin interface, available if
you are logged in at, e.g.:

  https://webapps.cspace.berkeley.edu/<tenant>/admin
  
Note that if changes are made online to the content of an item, steps may need to be taken to preserve those changes
when the project is updated: normally, the project update scripts (i.e. "deployment scripts") reload the fixture from
whatever is checked in to GitHub.

Below is a conversation that shows how to preserve changes to the nav items:

"""
# login to target server
jblowe:pahma_project jblowe$ ssh cspace-prod.cspace.berkeley.edu
Last login: Wed Jul 15 17:10:04 2015 from ucbvpn-208-65.vpn.berkeley.edu
# become webapp user
-sh-4.1$ sudo su - app_webapps
# start virtual environment
[app_webapps@cspace-prod-01 ~]$ venv
# switch to project for which you want to snag changes
(venv)[app_webapps@cspace-prod-01 ~]$ cd pahma
# dump the database table corresponding to the app of interest to the appropriate json file
(venv)[app_webapps@cspace-prod-01 pahma]$ python manage.py dumpdata --format=json search | python -mjson.tool > fixtures/searchApp.json
# check to see that it really is different stuff!
(venv)[app_webapps@cspace-prod-01 pahma]$ git status
[...]
#
#	modified:   fixtures/searchApp.json

# since we don't check in changes from deployed code, we need to move the file(s) to our local machine to
# check it into github. We do this by copying the file(s) first to /tmp so we can get to them from our developer account
(venv)[app_webapps@cspace-prod-01 pahma]$ cp fixtures/*.json /tmp
(venv)[app_webapps@cspace-prod-01 pahma]$ 

# Now, on our local machine:
$ cd ..../<project>/fixtures
fixtures $ scp cspace-prod.cspace.berkeley.edu:/tmp/*.json .
internalApp.json                                                                  100%  472     0.5KB/s   00:00    
searchApp.json                                                                    100%   10KB  10.1KB/s   00:01    
toolboxApp.json                                                                   100%  206     0.2KB/s   00:00    
uploadTricoder.json                                                               100% 7590     7.4KB/s   00:00    
fixtures jblowe$ git status
On branch master
Your branch is up-to-date with 'origin/master'.
Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git checkout -- <file>..." to discard changes in working directory)

	modified:   searchApp.json


# commit and push the changes
fixtures $ git commit -a -m "PAHMA-1337: capture updates to Help tab for search webapp"
fixtures $ git push -v
"""
