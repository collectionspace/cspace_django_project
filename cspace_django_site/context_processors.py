def settings(request):
    """
    Put selected settings variables into the default template context
    """
    from django.conf import settings
    return {
        'googleAnalytics': settings.GOOGLE_ANALYTICS,
    }
