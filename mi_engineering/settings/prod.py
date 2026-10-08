import os
from pathlib import Path
from django.core.exceptions import ImproperlyConfigured
from .base import *

# Production Secret Key validation
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")
if not SECRET_KEY:
    raise ImproperlyConfigured("DJANGO_SECRET_KEY environment variable is required in production.")

DEBUG = False

# Allowed Hosts
_allowed_hosts_raw = os.environ.get(
    "DJANGO_ALLOWED_HOSTS",
    os.environ.get("ALLOWED_HOSTS", "miengineeringworks.in,www.miengineeringworks.in,127.0.0.1,localhost"),
)
ALLOWED_HOSTS = [host.strip() for host in _allowed_hosts_raw.split(",") if host.strip()]

# CSRF Trusted Origins (Normalized with scheme)
_csrf_origins_raw = os.environ.get(
    "CSRF_TRUSTED_ORIGINS",
    "https://miengineeringworks.in,https://www.miengineeringworks.in",
)
CSRF_TRUSTED_ORIGINS = []
for origin in _csrf_origins_raw.split(","):
    origin = origin.strip()
    if not origin:
        continue
    if not origin.startswith(("http://", "https://")):
        origin = f"https://{origin}"
    CSRF_TRUSTED_ORIGINS.append(origin)

# Reverse Proxy SSL Header
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Cookie Security
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# HTTPS Redirect & HSTS
# When Nginx unconditionally redirects port 80 to 443, SECURE_SSL_REDIRECT can be False
# to allow internal health checks via 127.0.0.1:8000. It can be enabled via env if needed.
SECURE_SSL_REDIRECT = os.getenv("SECURE_SSL_REDIRECT", "False").lower() in ("true", "1", "t")
SECURE_HSTS_SECONDS = int(os.getenv("SECURE_HSTS_SECONDS", "31536000"))
SECURE_HSTS_INCLUDE_SUBDOMAINS = os.getenv("SECURE_HSTS_INCLUDE_SUBDOMAINS", "True").lower() in ("true", "1", "t")
SECURE_HSTS_PRELOAD = os.getenv("SECURE_HSTS_PRELOAD", "True").lower() in ("true", "1", "t")

# Database Configuration - SQLite in dedicated DB_DIR
_db_dir_env = os.environ.get("DB_DIR")
if _db_dir_env:
    _db_path = Path(_db_dir_env)
    DB_DIR = _db_path if _db_path.is_absolute() else BASE_DIR / _db_path
elif Path("/var/db").exists():
    DB_DIR = Path("/var/db")
else:
    DB_DIR = BASE_DIR / "data"

try:
    DB_DIR.mkdir(parents=True, exist_ok=True)
except Exception:
    pass

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": DB_DIR / "db.sqlite3",
        "OPTIONS": {
            "timeout": 20,
        },
    }
}

# Static Files Configuration
STATIC_URL = os.environ.get("STATIC_URL", "/static/")
if not STATIC_URL.endswith("/"):
    STATIC_URL += "/"

_prod_static_root = os.environ.get("STATIC_ROOT") or os.environ.get("STATIC_DIR")
if _prod_static_root:
    _static_path = Path(_prod_static_root)
    STATIC_ROOT = _static_path if _static_path.is_absolute() else BASE_DIR / _static_path
elif Path("/var/deployment/mi_engineering/staticfiles").exists():
    STATIC_ROOT = Path("/var/deployment/mi_engineering/staticfiles")
else:
    STATIC_ROOT = BASE_DIR / "staticfiles"

try:
    STATIC_ROOT.mkdir(parents=True, exist_ok=True)
except Exception:
    pass

# Media Files Configuration
MEDIA_URL = os.environ.get("MEDIA_URL", "/media/")
if not MEDIA_URL.endswith("/"):
    MEDIA_URL += "/"

_prod_media_root = os.environ.get("MEDIA_ROOT") or os.environ.get("MEDIA_DIR")
if _prod_media_root:
    _media_path = Path(_prod_media_root)
    MEDIA_ROOT = _media_path if _media_path.is_absolute() else BASE_DIR / _media_path
elif Path("/var/data/media").exists():
    MEDIA_ROOT = Path("/var/data/media")
else:
    MEDIA_ROOT = BASE_DIR / "media"

try:
    MEDIA_ROOT.mkdir(parents=True, exist_ok=True)
except Exception:
    pass

# Email / SMTP Configuration
EMAIL_BACKEND = os.getenv(
    "EMAIL_BACKEND",
    "django.core.mail.backends.smtp.EmailBackend",
)
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True").lower() in ("true", "1", "t")
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")

DEFAULT_FROM_EMAIL = os.getenv(
    "DEFAULT_FROM_EMAIL",
    f'"M.I. Engineering Works" <{EMAIL_HOST_USER}>' if EMAIL_HOST_USER else '"M.I. Engineering Works" <webmaster@miengineeringworks.in>',
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
