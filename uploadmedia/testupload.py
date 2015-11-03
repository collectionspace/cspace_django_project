import requests
from requests.auth import HTTPBasicAuth

filename = '9-22239a-c.JPG'
fullpath = '/tmp/image_upload_cache_ucjeps/9-22239a-c.JPG'
#payload = {'submit': 'OK', 'file': '@%s' % fullpath}
payload = {'submit': 'OK'}
url = 'https://ucjeps-dev.cspace.berkeley.edu/cspace-services/blobs'
username = 'jblowe@berkeley.edu'
password = 'pumpkins99'

files = {'file': (filename, open(fullpath, 'rb'), 'image/jpeg', {'Expires': '0'})}

response = requests.post(url, data=payload, files=files, auth=HTTPBasicAuth(username, password))
print response
