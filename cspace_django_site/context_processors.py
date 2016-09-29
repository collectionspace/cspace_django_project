def settings(request):
    """
    Put selected settings variables into the default template context
    """
    from django.conf import settings
    return {
        'UA_TRACKING_ID': settings.UA_TRACKING_ID,
    }
