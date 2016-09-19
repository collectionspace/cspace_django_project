__author__ = 'Julian Jaffe'

import unittest
import time, sys
import dbconnector
from common import cspace
from os import path
from cspace_django_site import settings


class ConnectorTestCase(unittest.TestCase):
    def test_connection(self):
        # No module level setUp function, so just run this first
        config = cspace.getConfig(path.join(settings.BASE_PARENT_DIR, 'config'), "testConnector")
        self.assertEqual(dbconnector.testDB(config), "OK")

    def test_setQuery(self):
        config = cspace.getConfig(path.join(settings.BASE_PARENT_DIR, 'config'), "testConnector")
        institution = config.get('info','institution')
        qualifier = ''
        location = ''
        updateType = 'inventory'
        query = dbconnector.setquery('inventory', location, qualifier, institution)

        elapsedtime = time.time()
        locations = dbconnector.getlocations(location, location, 10, config, updateType, institution)
        elapsedtime = time.time() - elapsedtime
        sys.stderr.write('all objects: %s :: %s\n' % (location, elapsedtime))
        self.assertEqual(len(locations), 0)


if __name__ == '__main__':
    unittest.main()
