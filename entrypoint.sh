#!/usr/bin/env bash

set -e

echo "Creating latest migrations..."
uv run python manage.py makemigrations --noinput

echo "Applying database migrations..."
uv run python manage.py migrate --noinput

echo "Collecting static files..."
uv run python manage.py collectstatic --noinput

echo "Starting Django with Gunicorn..."

exec uv run gunicorn mi_engineering.wsgi:application \
    --bind "0.0.0.0:${PORT:-8000}" \
    --workers "${WEB_CONCURRENCY:-4}" \
    --timeout "${GUNICORN_TIMEOUT:-120}" \
    --access-logfile - \
    --error-logfile -