__author__ = 'remillet'
"""
Please see the README.txt file in this package directory for the documentation of this module.
"""

from os import path
from django.contrib.auth.models import User
from common import cspace
import logging

#
# Get our logger instance for this module
#
logger = logging.getLogger(__name__)

HTTP_PROTOCOL = "http"
CSPACE_AUTHN_CONFIG_FILENAME = 'authn'

CONFIGSECTION_AUTHN_CONNECT = 'connect'  # The [connect] section of the config file
CONFIGSECTION_AUTHN_INFO = 'info'  # The [info] section of the config file
CSPACE_AUTHN_OVERRIDE_PROPERTY = 'override'


def getConfigOption(config, property_name):
    """
    This is a utility method that returns a CONFIGSECTION_AUTHN_CONNECT config section of a configuration file.
    """
    return cspace.getConfigOptionWithSection(config, CONFIGSECTION_AUTHN_CONNECT, property_name)


class CSpaceAuthN(object):
    config = None
    overrideWithConfig = False
    handleAuthNRequest = None  # a callback method to the main site
    configFileUsed = False
    realm = None
    uri = None
    hostname = None
    protocol = None
    port = None
    authNDictionary = dict()

    def __init__(self):
        #
        # Empty constructor
        #
        return

    @classmethod
    def resetPasswordCache(cls):
        cls.authNDictionary = dict()  # A dictionary of cached passwords

    @classmethod
    def initialize(cls, handleAuthNRequest, clearPasswordCache=False):
        """

        :param handleAuthNRequest:
        :param clearPasswordCache:
        """
        if handleAuthNRequest:
            cls.handleAuthNRequest = handleAuthNRequest  # a delegate method that gets called by our AuthN method

        if clearPasswordCache:
            CSpaceAuthN.resetPasswordCache()

        cls.config = cspace.getConfig(path.dirname(__file__), CSPACE_AUTHN_CONFIG_FILENAME)
        if cspace.getConfigOptionWithSection(cls.config, CONFIGSECTION_AUTHN_INFO, CSPACE_AUTHN_OVERRIDE_PROPERTY) \
                == "True":
            cls.overrideWithConfig = True
        else:
            cls.overrideWithConfig = False

    def isSetup(self):
        """
            This method tests to see if the required fields are all set.
        :type self: CSpaceAuthN
        :return:
        """
        result = True
        isMissingProperties = False
        errMsg = "The property/option %s must be set to a valid value."

        if self.realm is None:
            isMissingProperties = True
            logger.error(errMsg % cspace.CSPACE_REALM_PROPERTY)
        if self.uri is None:
            isMissingProperties = True
            logger.error(errMsg % cspace.CSPACE_URI_PROPERTY)
        if self.hostname is None:
            isMissingProperties = True
            logger.error(errMsg % cspace.CSPACE_HOSTNAME_PROPERTY)
        if self.protocol is None:
            isMissingProperties = True
            logger.error(errMsg % cspace.CSPACE_PROTOCOL_PROPERTY)
        if self.port is None:
            isMissingProperties = True
            logger.error(errMsg % cspace.CSPACE_PORT_PROPERTY)
        if self.authNDictionary is None:
            isMissingProperties = True
            logger.error(errMsg % "CSpaceAuthN.authNDictionary")

        if isMissingProperties is True:
            result = False

        return result

    def setupForRequest(self):
        """
            This constructor will look for a config file named authn.cfg that must be a directory sibling of this class
            file.  If the class static property members have not already been set by the class method initialize()
            or the 'override' property is True then the values in the config file will be used.
        """

        if self.handleAuthNRequest is not None:
            self.handleAuthNRequest(self)  # Give our delegate a chance to setup our connection params by calling it

        if self.isSetup() is True and self.overrideWithConfig is False:
            return  # The delegate set all the params and we're not configured to override the delegate

        try:
            if self.realm is None or self.overrideWithConfig:
                self.realm = getConfigOption(self.config, cspace.CSPACE_REALM_PROPERTY)
                self.configFileUsed = True

            if self.uri is None or self.overrideWithConfig:
                self.uri = getConfigOption(self.config, cspace.CSPACE_URI_PROPERTY)
                self.configFileUsed = True

            if self.hostname is None or self.overrideWithConfig:
                self.hostname = getConfigOption(self.config, cspace.CSPACE_HOSTNAME_PROPERTY)
                self.configFileUsed = True

            if self.protocol is None or self.overrideWithConfig:
                self.protocol = getConfigOption(self.config, cspace.CSPACE_PROTOCOL_PROPERTY)
                self.configFileUsed = True

            if self.port is None or self.overrideWithConfig:
                self.port = getConfigOption(self.config, cspace.CSPACE_PORT_PROPERTY)
                self.configFileUsed = True

        except Exception as e:
            logger.warning("The CSpaceAuthN authenticate back-end config file %s was missing." %
                           CSPACE_AUTHN_CONFIG_FILENAME + cspace.CONFIG_SUFFIX)
            logger.warning(e) # Log the exception as well.

        if self.isSetup() is False:
            errMsg = "The CSpaceAuthN Django authentication back-end was not properly initialized.  \
            Please check the log files for details."
            raise Exception(errMsg)

    def authenticateWithCSpace(self, username=None, password=None):
        """
            Attempts to authenticate with a CollectionSpace Services instance.  Reads the URI, Realm, hostname from a
            config file name authn.cfg
        :param username:
        :param password:
        """
        result = False

        self.setupForRequest()
        (url, data, statusCode) = cspace.make_get_request(self.realm, self.uri, self.hostname, self.protocol, self.port,
                                                          username, password)
        logger.info("Request to %s: %s" % (url, statusCode))
        if statusCode is 200:
            result = True

        if result:
            logger.debug('User: %s authenticated with Host: %s' % (username, self.hostname))
        else:
            logger.debug('User: %s could not authenticate with Host: %s' % (username, self.hostname))

        return result

    def getCSpacePassword(self, username):
        result = None
        if self.authNDictionary is not None:
            result = self.authNDictionary[username]  # If they're a cspace user that's been authenticated, then we
        return result

    def setCSpacePassword(self, username, password):
        self.authNDictionary[username] = password

    #
    # Django AuthN/AuthZ methods to implement.
    #

    def authenticate(self, username=None, password=None):
        """
            Called by Django's AuthN/AuthZ framework to authenticate a user with username and password credentials.
            This method attempts to authenticate with the specified CollectionSpace Services instance.  If authenti-
            cation is successful then the cspace user is added to Django's built-in User list with *no* password.  The
            cspace password is simply cached in this classes (CSpaceAuthN) 'authNDictionary' dictionary.

            *** NOTE *** If the cspace user's password changes in the back-end (in the CollectionSpace system) then any
            attempt by the application to use the cached password to connect to the back-end will fail until the user
            logs out and logs back in with the updated/correct password.
        """
        result = None
        # Check the username/password and return a User.
        authenticatedWithCSpace = self.authenticateWithCSpace(username=username, password=password)
        if authenticatedWithCSpace is True:
            try:
                result = User.objects.get(username=username)
            except User.DoesNotExist:
                newUser = User(username=username, password='none')
                newUser.is_staff = True
                newUser.is_superuser = True
                newUser.save()
                result = newUser

        if result is not None:
            self.setCSpacePassword(username, password)
            result.cspace_password = password

        return result

    def get_user(self, user_id):
        """
            Called by Django's AuthN/AuthZ framework to get the User instance from a user ID.

            *** NOTE *** If the cspace user's password changes in the back-end (in the CollectionSpace system) then any
            attempt by the application to use the cached password to connect to the back-end will fail until the user
            logs out and logs back in with the updated/correct password.
        """
        try:
            user = User.objects.get(pk=user_id)  # Lookup the user from Django's built-in list of users
            username = user.username
            passwd = self.getCSpacePassword(username)
            # should already have their password cached
            if passwd is not None:
                user.cspace_password = passwd  # Attach the user's cspace password to the User instance
            else:
                user = None  # If for some unknown reason the password is null, we should return the 'None'
        except User.DoesNotExist:
            user = None
        except IndexError:
            user = None
        except KeyError:
            user = None

        return user
