import os
from pathlib import Path
from .base import *

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")

DEBUG = False

ALLOWED_HOSTS = [
    host.strip() for host in os.environ.get(
        "DJANGO_ALLOWED_HOSTS",
        "miengineeringworks.in,www.miengineeringworks.in",
    ).split(",") if host.strip()
]

CSRF_TRUSTED_ORIGINS = [
    "https://miengineeringworks.in",
    "https://www.miengineeringworks.in",
]

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Database - SQLite
DB_DIR = Path(os.environ.get(
    "DB_DIR",
    BASE_DIR / "data",
))

DB_DIR.mkdir(parents=True, exist_ok=True)

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": DB_DIR / "db.sqlite3",
    }
}

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
    f"M.I. Engineering Works <{EMAIL_HOST_USER}>",
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
