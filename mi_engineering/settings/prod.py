import os
from .base import *

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')

DEBUG = False

# Parse list of allowed hosts safely from environment
ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get('DJANGO_ALLOWED_HOSTS', '').split(',')
    if host.strip()
]

# Email Configuration
EMAIL_BACKEND = os.getenv("EMAIL_BACKEND",
                          "django.core.mail.backends.smtp.EmailBackend")
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS",
                          "True").lower() in ("true", "1", "t")
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL",
                               f"M.I. Engineering Works <{EMAIL_HOST_USER}>")

if "MAILERS" in globals():
    del MAILERS  # type: ignore
