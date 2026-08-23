from .base import *

SECRET_KEY = 'django-insecure-k$ab5r24i-tr_0r15ihfn2p=)-=!h@t@lwu84=#bjw$)!y15n8'

DEBUG = True

ALLOWED_HOSTS = []

MAILERS = {
    'default': {
        'BACKEND': 'django.core.mail.backends.console.EmailBackend',
    },
}