import requests
from requests.auth import HTTPBasicAuth

# use this script to test your ability to POST an image to the blobs service
# you'll need to find an image file and put it in a local directory.
#
# the nice thing about this script is that it tests permission on local
# directories and files as well as connectivity to server and authentication.

filename = '9-22239a-c.JPG'
fullpath = '/tmp/image_upload_cache_ucjeps/9-22239a-c.JPG'
#payload = {'submit': 'OK', 'file': '@%s' % fullpath}
payload = {'submit': 'OK'}
url = 'https://ucjeps-dev.cspace.berkeley.edu/cspace-services/blobs'
username = 'xxxx@berkeley.edu'
password = 'xxxx'

files = {'file': (filename, open(fullpath, 'rb'), 'image/jpeg', {'Expires': '0'})}

response = requests.post(url, data=payload, files=files, auth=HTTPBasicAuth(username, password))
print response
