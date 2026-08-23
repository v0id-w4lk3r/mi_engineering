import os
from .base import *

# Pull secure keys and variables from environment variables in production
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')

DEBUG = False

ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '').split(',')

# Configure production email service (e.g., SMTP)
MAILERS = {
    'default': {
        'BACKEND': 'django.core.mail.backends.smtp.EmailBackend',
        'HOST': os.environ.get('EMAIL_HOST', 'smtp.gmail.com'),
        'PORT': os.environ.get('EMAIL_PORT', 587),
        'USE_TLS': True,
        'USER': os.environ.get('EMAIL_HOST_USER'),
        'PASSWORD': os.environ.get('EMAIL_HOST_PASSWORD'),
    },
}