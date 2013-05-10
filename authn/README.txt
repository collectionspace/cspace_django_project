This Python package provides a custom Django authentication "back-end" for connecting to a CollectionSpace Services
instance. For more details on how to customize Django's authentication mechanism read the information at the following
link: https://docs.djangoproject.com/en/dev/topics/auth/customizing/

To configure your Django site/project to use this custom authentication "back-end", add the full qualified "CSpaceAuthN"
class name to the "AUTHENTICATION_BACKENDS" variable in your Django site's main .settings file.  For example,

#
# AuthN backends
#
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend', # the default "Admin" AuthN provider
    'authn.authn.CSpaceAuthN',
)

Before Django can use the "CSpaceAuthN" backend successfully, the "CSpaceAuthN" class needs to be initialized
to connect to a CollectionSpace Services instance. You can configure the how the "CSpaceAuthN" gets initialized two
different ways:

1. Modify the values under the "[cspace_authn_connect]" section of the "/cspace_django_project/cspace_django_site/main.cfg" file.

OR

2. Modify the values under the "[]" section of the "/cspace_django_site/authn/authn.cfg" file.

The values in step 1 will override the values in step 2 -i.e., the values in the main.cfg will override the values in
authn.cfg.

To allow more flexibility in how this AuthN back-end is initialized, the current code also supports the following:
If some of the values from the main.cfg files are missing or empty then the corresponding non-missing,
non-empty values in the authn.cfg will be used.  Also, if the "override" property in the authn.cfg file is set to "True" then
the values in authn.cfg will override those of the main.cfg file.


