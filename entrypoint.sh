#!/usr/bin/env bash

set -e

WORKERS="${WEB_CONCURRENCY:-$(( $(nproc) * 2 + 1 ))}"

echo "Creating latest migrations..."
uv run python manage.py makemigrations --noinput

echo "Applying database migrations..."
uv run python manage.py migrate --noinput

echo "Collecting static files..."
uv run python manage.py collectstatic --noinput

echo "Starting Django with Gunicorn..."
echo "Workers: ${WORKERS}"
echo "Listening on: 127.0.0.1:${PORT:-8000}"

exec uv run gunicorn mi_engineering.wsgi:application \
    --bind "127.0.0.1:${PORT:-8000}" \
    --workers "${WORKERS}" \
    --timeout "${GUNICORN_TIMEOUT:-120}" \
    --access-logfile - \
    --error-logfile -