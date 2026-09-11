#!/usr/bin/env bash

set -e

PORT="${PORT:-8000}"
WORKERS="${WEB_CONCURRENCY:-4}"
TIMEOUT="${GUNICORN_TIMEOUT:-120}"

export DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-mi_engineering.settings.prod}"

echo "Checking Django..."
uv run python manage.py check

echo "Creating migrations..."
uv run python manage.py makemigrations accounts home gallery products --noinput

echo "Applying migrations..."
uv run python manage.py migrate --noinput

echo "Building Tailwind CSS..."
bun run build:css

echo "Collecting static files..."
# Ignores input.css so WhiteNoise does not fail on @import "tailwindcss"
uv run python manage.py collectstatic --noinput -i "css/input.css"

echo "Setting static files permissions for Nginx..."
STATIC_ROOT=$(uv run python -c "from django.conf import settings; print(settings.STATIC_ROOT)")
if [ -d "$STATIC_ROOT" ]; then
    chmod -R 755 "$STATIC_ROOT"
    find "$STATIC_ROOT" -type f -exec chmod 644 {} +
fi

echo "Starting Gunicorn on 127.0.0.1:${PORT}..."

exec uv run gunicorn mi_engineering.wsgi:application \
    --bind "127.0.0.1:${PORT}" \
    --workers "${WORKERS}" \
    --timeout "${TIMEOUT}" \
    --access-logfile - \
    --error-logfile -
