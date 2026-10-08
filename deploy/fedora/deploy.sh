#!/usr/bin/env bash
# ==============================================================================
# M.I. Engineering Works - Fedora Initial / Full Deployment Script
# Deploys application code, sets up .env, dependencies, migrations, SSL, and Nginx.
# ==============================================================================

set -Eeuo pipefail

if [ "$(id -u)" -ne 0 ]; then
    echo "ERROR: This script must be run as root (use sudo)." >&2
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
TARGET_DIR="/var/deployment/mi_engineering"
CERTBOT_EMAIL="${1:-admin@miengineeringworks.in}"

echo "==> [Fedora Deploy] Starting deployment to $TARGET_DIR..."

# 1. Sync Code to Deployment Directory if running from separate clone
if [ "$REPO_ROOT" != "$TARGET_DIR" ]; then
    echo "==> [Fedora Deploy] Synchronizing code from $REPO_ROOT to $TARGET_DIR..."
    mkdir -p "$TARGET_DIR"
    rsync -av --exclude='.git' --exclude='.env' --exclude='.venv' --exclude='data' --exclude='media' "$REPO_ROOT/" "$TARGET_DIR/"
fi

# Set proper ownership
chown -R syn:webhost "$TARGET_DIR"
chown -R syn:webhost /var/db /var/data

# 2. Environment Configuration (.env)
if [ ! -f "$TARGET_DIR/.env" ]; then
    echo "==> [Fedora Deploy] Generating new production .env from template..."
    if [ -f "$TARGET_DIR/.env.example" ]; then
        cp "$TARGET_DIR/.env.example" "$TARGET_DIR/.env"
    elif [ -f "$TARGET_DIR/example.env" ]; then
        cp "$TARGET_DIR/example.env" "$TARGET_DIR/.env"
    else
        echo "ERROR: Neither .env.example nor example.env found!" >&2
        exit 1
    fi

    # Generate a strong cryptographic secret key
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(50))")
    sed -i "s|^DJANGO_SECRET_KEY=.*|DJANGO_SECRET_KEY=${SECRET_KEY}|" "$TARGET_DIR/.env"
    echo "Generated unique production DJANGO_SECRET_KEY."
else
    echo "==> [Fedora Deploy] Existing .env found. Preserving without modification."
fi

# Secure .env permissions
chmod 600 "$TARGET_DIR/.env"
chown syn:webhost "$TARGET_DIR/.env"

# 3. Install/Sync Dependencies with uv as user 'syn'
echo "==> [Fedora Deploy] Syncing Python dependencies using uv..."
sudo -u syn -H /bin/bash -c "cd '$TARGET_DIR' && /usr/local/bin/uv sync --frozen 2>/dev/null || /usr/local/bin/uv sync"

# 4. Run Migrations & Collect Static
echo "==> [Fedora Deploy] Running database migrations..."
sudo -u syn -H /bin/bash -c "cd '$TARGET_DIR' && /usr/local/bin/uv run python manage.py migrate --noinput"

echo "==> [Fedora Deploy] Collecting static files..."
sudo -u syn -H /bin/bash -c "cd '$TARGET_DIR' && /usr/local/bin/uv run python manage.py collectstatic --noinput -i 'css/input.css'"

# Fix directory permissions
chmod -R u=rwX,go=rX "$TARGET_DIR/staticfiles" 2>/dev/null || true
chmod -R u=rwX,g=rwXs,o=rX /var/data/media 2>/dev/null || true

# 5. Start / Restart Gunicorn Application Service
echo "==> [Fedora Deploy] Starting application service..."
systemctl restart mi_engineering.service

# Wait for service to initialize
sleep 3

# Verify local loopback response
if curl -s -f -o /dev/null -m 5 "http://127.0.0.1:8000/" || curl -s -o /dev/null -m 5 "http://127.0.0.1:8000/"; then
    echo "Gunicorn is running and responding on 127.0.0.1:8000."
else
    echo "WARNING: Gunicorn did not respond within 5 seconds. Checking journal logs:"
    journalctl -u mi_engineering.service -n 20 --no-pager
fi

# 6. SSL Certificate Verification & Issuance
CERT_PATH="/etc/letsencrypt/live/miengineeringworks.in/fullchain.pem"
if [ ! -f "$CERT_PATH" ]; then
    echo "==> [Fedora Deploy] No SSL certificate found. Requesting via Certbot webroot..."
    if certbot certonly --webroot -w /var/www/certbot \
        -d miengineeringworks.in -d www.miengineeringworks.in \
        --non-interactive --agree-tos -m "$CERTBOT_EMAIL"; then
        echo "SSL certificate successfully obtained."
    else
        echo "WARNING: Certbot failed to obtain certificates. Leaving HTTP bootstrap active." >&2
        echo "Check DNS resolution for miengineeringworks.in and run certbot manually." >&2
    fi
fi

# 7. Switch to Production HTTPS Nginx Config if certificates exist
if [ -f "$CERT_PATH" ]; then
    echo "==> [Fedora Deploy] Applying production HTTPS Nginx configuration..."
    cp "$SCRIPT_DIR/nginx.conf" /etc/nginx/conf.d/mi_engineering.conf
    nginx -t
    systemctl reload nginx
    echo "Nginx reloaded with SSL configuration."
fi

# 8. Re-apply SELinux contexts
if command -v restorecon >/dev/null 2>&1; then
    restorecon -Rv "$TARGET_DIR/staticfiles" /var/data/media /var/www/certbot 2>/dev/null || true
fi

echo "==> [Fedora Deploy] Deployment completed successfully!"
