# import os
from .base import *

DEBUG = True

# Explicitly allow local development hosts
ALLOWED_HOSTS = ['*']

# SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY',
#                             'django-insecure-dev-key-change-in-production')

MAILERS = {
    'default': {
        'BACKEND': 'django.core.mail.backends.console.EmailBackend',
    },
}
