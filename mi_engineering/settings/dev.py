from .base import *

DEBUG = True

SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "django-insecure-dev-key-local-only-never-use-in-production-1234567890",
)

ALLOWED_HOSTS = ['*']