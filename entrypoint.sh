#!/usr/bin/env bash
# ==============================================================================
# M.I. Engineering Works - Production Entrypoint Script
# Handles migrations, static collection, permissions, and Gunicorn execution.
# ==============================================================================

set -Eeuo pipefail

# Ensure group-writable permissions for newly created files/directories
umask 0002

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Configuration defaults
PORT="${PORT:-8000}"
WORKERS="${WEB_CONCURRENCY:-4}"
TIMEOUT="${GUNICORN_TIMEOUT:-120}"
export DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-mi_engineering.settings.prod}"

# Locate Python and runner (uv or virtualenv)
if command -v uv >/dev/null 2>&1; then
    RUNNER="uv run"
    PYTHON_CMD="uv run python"
    GUNICORN_CMD="uv run gunicorn"
elif [ -x "/usr/local/bin/uv" ]; then
    RUNNER="/usr/local/bin/uv run"
    PYTHON_CMD="/usr/local/bin/uv run python"
    GUNICORN_CMD="/usr/local/bin/uv run gunicorn"
elif [ -x "$SCRIPT_DIR/.venv/bin/python" ]; then
    RUNNER=""
    PYTHON_CMD="$SCRIPT_DIR/.venv/bin/python"
    GUNICORN_CMD="$SCRIPT_DIR/.venv/bin/gunicorn"
else
    echo "ERROR: Neither 'uv' nor local virtualenv Python found in $SCRIPT_DIR/.venv" >&2
    exit 1
fi

echo "==> Validating Django production configuration..."
$PYTHON_CMD manage.py check

echo "==> Ensuring database directory exists..."
DB_DIR_VAL=$($PYTHON_CMD -c "from django.conf import settings; print(getattr(settings, 'DB_DIR', ''))" 2>/dev/null || true)
if [ -n "$DB_DIR_VAL" ] && [ ! -d "$DB_DIR_VAL" ]; then
    mkdir -p "$DB_DIR_VAL" 2>/dev/null || true
fi

echo "==> Applying database migrations..."
$PYTHON_CMD manage.py migrate --noinput

echo "==> Collecting static assets..."
# Ignore raw Tailwind source to prevent manifest parser errors
$PYTHON_CMD manage.py collectstatic --noinput -i "css/input.css"

echo "==> Setting static files permissions for Nginx..."
STATIC_ROOT=$($PYTHON_CMD -c "from django.conf import settings; print(getattr(settings, 'STATIC_ROOT', ''))" 2>/dev/null || true)
if [ -n "$STATIC_ROOT" ] && [ -d "$STATIC_ROOT" ]; then
    chmod -R u=rwX,go=rX "$STATIC_ROOT" 2>/dev/null || true
fi

echo "==> Ensuring media upload directory permissions..."
MEDIA_ROOT=$($PYTHON_CMD -c "from django.conf import settings; print(getattr(settings, 'MEDIA_ROOT', ''))" 2>/dev/null || true)
if [ -n "$MEDIA_ROOT" ]; then
    mkdir -p "$MEDIA_ROOT" 2>/dev/null || true
    chmod -R u=rwX,g=rwXs,o=rX "$MEDIA_ROOT" 2>/dev/null || true
fi

echo "==> Starting Gunicorn on 127.0.0.1:${PORT} (${WORKERS} workers, ${TIMEOUT}s timeout)..."
exec $GUNICORN_CMD mi_engineering.wsgi:application \
    --bind "127.0.0.1:${PORT}" \
    --workers "${WORKERS}" \
    --timeout "${TIMEOUT}" \
    --access-logfile - \
    --error-logfile -
