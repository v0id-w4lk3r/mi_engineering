#!/usr/bin/env bash

set -e

PORT="${PORT:-8000}"
WORKERS="${WEB_CONCURRENCY:-4}"
TIMEOUT="${GUNICORN_TIMEOUT:-120}"

export DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-mi_engineering.settings.prod}"

echo "Checking Django..."
uv run python manage.py check

echo "Creating migrations..."
uv run python manage.py makemigrations --noinput

echo "Applying migrations..."
uv run python manage.py migrate --noinput

echo "Collecting static files..."
uv run python manage.py collectstatic --noinput

echo "Starting Gunicorn on 127.0.0.1:${PORT}..."

exec uv run gunicorn mi_engineering.wsgi:application \
    --bind "127.0.0.1:${PORT}" \
    --workers "${WORKERS}" \
    --timeout "${TIMEOUT}" \
    --access-logfile - \
    --error-logfile -