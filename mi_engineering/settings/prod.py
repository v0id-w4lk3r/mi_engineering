import os
from pathlib import Path
from django.core.exceptions import ImproperlyConfigured
from .base import *

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")
if not SECRET_KEY:
    raise ImproperlyConfigured("DJANGO_SECRET_KEY environment variable is required in production.")

DEBUG = False

ALLOWED_HOSTS = [
    host.strip() for host in os.environ.get(
        "DJANGO_ALLOWED_HOSTS",
        os.environ.get("ALLOWED_HOSTS", "miengineeringworks.in,www.miengineeringworks.in"),
    ).split(",") if host.strip()
]

CSRF_TRUSTED_ORIGINS = [
    origin.strip() for origin in os.environ.get(
        "CSRF_TRUSTED_ORIGINS",
        "https://miengineeringworks.in,https://www.miengineeringworks.in",
    ).split(",") if origin.strip()
]

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_CONTENT_TYPE_NOSNIFF = True

SECURE_SSL_REDIRECT = os.getenv("SECURE_SSL_REDIRECT", "True").lower() in ("true", "1", "t")
SECURE_HSTS_SECONDS = int(os.getenv("SECURE_HSTS_SECONDS", "31536000"))
SECURE_HSTS_INCLUDE_SUBDOMAINS = os.getenv("SECURE_HSTS_INCLUDE_SUBDOMAINS", "True").lower() in ("true", "1", "t")
SECURE_HSTS_PRELOAD = os.getenv("SECURE_HSTS_PRELOAD", "True").lower() in ("true", "1", "t")

# Database - SQLite with concurrency timeout
_db_dir_env = os.environ.get("DB_DIR")
if _db_dir_env:
    _db_path = Path(_db_dir_env)
    DB_DIR = _db_path if _db_path.is_absolute() else BASE_DIR / _db_path
else:
    DB_DIR = BASE_DIR / "data"

DB_DIR.mkdir(parents=True, exist_ok=True)

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": DB_DIR / "db.sqlite3",
        "OPTIONS": {
            "timeout": 20,
        },
    }
}

# Media Files Configuration (Configured via Environment Variables)
MEDIA_URL = os.environ.get("MEDIA_URL", "/media/")
if not MEDIA_URL.endswith("/"):
    MEDIA_URL += "/"

_prod_media_root = os.environ.get("MEDIA_ROOT") or os.environ.get("MEDIA_DIR")
if _prod_media_root:
    _media_path = Path(_prod_media_root)
    MEDIA_ROOT = _media_path if _media_path.is_absolute() else BASE_DIR / _media_path
else:
    MEDIA_ROOT = BASE_DIR / "media"

MEDIA_ROOT.mkdir(parents=True, exist_ok=True)

# Email Configuration
EMAIL_BACKEND = os.getenv(
    "EMAIL_BACKEND",
    "django.core.mail.backends.smtp.EmailBackend",
)

EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))

EMAIL_USE_TLS = os.getenv(
    "EMAIL_USE_TLS",
    "True",
).lower() in ("true", "1", "t")

EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")

DEFAULT_FROM_EMAIL = os.getenv(
    "DEFAULT_FROM_EMAIL",
    f'"M.I. Engineering Works" <{EMAIL_HOST_USER}>',
)

# Logging
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "django.request": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": False,
        },
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

if "MAILERS" in globals():
    del MAILERS
