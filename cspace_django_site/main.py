from os import path
from authn.authn import CSpaceAuthN
from common import cspace
import logging

logger = logging.getLogger(__name__)

class cspace_django_site:
    """

    """
    should_reload_config = False
    should_reload_authn_config = False
    is_initialized = False
    config = None

    @classmethod
    def loadConfig(cls):
        result = cspace.getConfig(path.dirname(__file__), "main")
        return result

    @classmethod
    def shouldInitialize(cls):
        """


        :return:
        """
        result = False
        if cspace_django_site.is_initialized is False or cspace_django_site.should_reload_config is True:
            result = True
        return result

    @classmethod
    def initialize_authn(cls, config, authNInstance):
        cls.should_reload_authn_config = cspace.getConfigOptionWithSection(cls.config,
                                                                           cspace.CONFIGSECTION_AUTHN_CONNECT,
                                                                           cspace.CSPACE_SHOULD_RELOAD_CONFIG)
        CSpaceAuthN.initialize(cls.handleAuthNRequest)
        if config and authNInstance:
            #
            # Read the required params from the config file
            #
            authNInstance.realm = cspace.getConfigOptionWithSection(config,
                                                                    cspace.CONFIGSECTION_AUTHN_CONNECT,
                                                                    cspace.CSPACE_REALM_PROPERTY)
            authNInstance.uri = cspace.getConfigOptionWithSection(config,
                                                                  cspace.CONFIGSECTION_AUTHN_CONNECT,
                                                                  cspace.CSPACE_URI_PROPERTY)
            authNInstance.hostname = cspace.getConfigOptionWithSection(config,
                                                                       cspace.CONFIGSECTION_AUTHN_CONNECT,
                                                                       cspace.CSPACE_HOSTNAME_PROPERTY)
            authNInstance.protocol = cspace.getConfigOptionWithSection(config,
                                                                       cspace.CONFIGSECTION_AUTHN_CONNECT,
                                                                       cspace.CSPACE_PROTOCOL_PROPERTY)
            authNInstance.port = cspace.getConfigOptionWithSection(config,
                                                                   cspace.CONFIGSECTION_AUTHN_CONNECT,
                                                                   cspace.CSPACE_PORT_PROPERTY)
            logger.info('AuthN initialized')

    @classmethod
    def handleAuthNRequest(cls, authnInstance):
        if cls.should_reload_authn_config:
            cls.config = cls.loadConfig()
        cls.initialize_authn(cls.config, authnInstance)

    @classmethod
    def initialize(cls):
        """
            Initializes our site.

        """
        if cspace_django_site.shouldInitialize() is False:
            logger.warning('Reinitializing the site.')

        cls.config = cls.loadConfig()
        cls.should_reload_config = cspace.getConfigOptionWithSection(cls.config, cspace.CONFIGSECTION_INFO,
                                                                     cspace.CSPACE_SHOULD_RELOAD_CONFIG)
        cls.initialize_authn(None, None)
        cls.is_initialized = True

    def __init__(self):
        """
            This is the class' default constructor.  Only 1 instance of this class should ever be created.
        """
        if cspace_django_site.shouldInitialize() is True:
            cspace_django_site.initialize()

    @classmethod
    def getConfig(cls):
        """
            Returns our site's config file.  Will also re-initialize the site if it is configured to do so.
        :return:
        """
        if cspace_django_site.shouldInitialize() is True:
            cspace_django_site.initialize()

        return cspace_django_site.config
