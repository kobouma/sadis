from .base import *  # noqa
DEBUG = True
REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] += ["rest_framework.renderers.BrowsableAPIRenderer"]  # noqa
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
ALLOWED_HOSTS = ['*']  # dev seulement — jamais en production
