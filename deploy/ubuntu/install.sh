#!/usr/bin/env bash
# ==============================================================================
# M.I. Engineering Works - Ubuntu Server Provisioning & Installation Script
# Supports: Ubuntu 22.04 LTS / 24.04 LTS
# Idempotent: Can be run multiple times safely.
# ==============================================================================

set -Eeuo pipefail

# 1. Root & OS Verification
if [ "$(id -u)" -ne 0 ]; then
    echo "ERROR: This script must be run as root (use sudo)." >&2
    exit 1
fi

if [ ! -f /etc/os-release ]; then
    echo "ERROR: Cannot detect operating system (/etc/os-release missing)." >&2
    exit 1
fi

# shellcheck source=/dev/null
. /etc/os-release
if [[ "${ID:-}" != "ubuntu" && "${ID_LIKE:-}" != *"debian"* && "${ID_LIKE:-}" != *"ubuntu"* ]]; then
    echo "ERROR: This installation script is designed for Ubuntu Server." >&2
    echo "Detected: ${PRETTY_NAME:-$ID}" >&2
    echo "For Fedora Server, please use deploy/fedora/install.sh instead." >&2
    exit 1
fi

echo "==> [Ubuntu] Starting system installation on ${PRETTY_NAME}..."

# 2. Package Installation via APT
echo "==> [Ubuntu] Updating package index and installing dependencies via APT..."
export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    build-essential \
    git \
    nginx \
    certbot \
    python3-certbot-nginx \
    ufw \
    curl \
    tar \
    rsync

# 3. Ensure uv is installed globally
if ! command -v uv >/dev/null 2>&1; then
    echo "==> [Ubuntu] Installing uv package manager..."
    curl -LsSf https://astral.sh/uv/install.sh | env UV_INSTALL_DIR="/usr/local/bin" sh
    chmod 755 /usr/local/bin/uv || true
else
    echo "==> [Ubuntu] uv is already installed at $(command -v uv)."
fi

# 4. User and Group Management (syn:webhost)
echo "==> [Ubuntu] Configuring application user and group..."
groupadd -f webhost

if ! id -u syn >/dev/null 2>&1; then
    useradd -m -g webhost -s /bin/bash syn
    echo "Created deployment user 'syn' in group 'webhost'."
else
    usermod -g webhost syn
fi

# Add Ubuntu Nginx user (www-data) to webhost group
usermod -aG webhost www-data

# 5. Directory Layout Setup
echo "==> [Ubuntu] Creating production directory layout..."
mkdir -p /var/deployment/mi_engineering
mkdir -p /var/db
mkdir -p /var/data/media
mkdir -p /var/deployment/mi_engineering/staticfiles
mkdir -p /var/www/certbot

# Set ownership and base permissions
chown -R syn:webhost /var/deployment
chown -R syn:webhost /var/db
chown -R syn:webhost /var/data
chown -R www-data:www-data /var/www/certbot

chmod 750 /var/deployment
chmod 750 /var/deployment/mi_engineering
chmod 750 /var/db
chmod 775 /var/data/media
chmod g+s /var/data/media  # Newly uploaded files inherit webhost group
chmod 755 /var/www/certbot

# 6. UFW Firewall Configuration
echo "==> [Ubuntu] Configuring UFW firewall..."
if command -v ufw >/dev/null 2>&1; then
    ufw allow OpenSSH || true
    ufw allow 'Nginx Full' || (ufw allow 80/tcp && ufw allow 443/tcp) || true
    # Enable UFW without interactive prompt if not already active
    if ! ufw status | grep -q "Status: active"; then
        echo "y" | ufw enable || true
    fi
fi

# 7. Systemd Service Installation
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "==> [Ubuntu] Installing systemd unit file..."
cp "$SCRIPT_DIR/mi_engineering.service" /etc/systemd/system/mi_engineering.service
chmod 644 /etc/systemd/system/mi_engineering.service
systemctl daemon-reload
systemctl enable mi_engineering.service

# 8. Nginx Bootstrap Setup (HTTP-only)
echo "==> [Ubuntu] Installing Nginx bootstrap configuration..."
# Remove default site if present
rm -f /etc/nginx/sites-enabled/default

cp "$SCRIPT_DIR/nginx.bootstrap.conf" /etc/nginx/sites-available/miengineeringworks.in.conf
ln -sf /etc/nginx/sites-available/miengineeringworks.in.conf /etc/nginx/sites-enabled/

# Test and start Nginx
nginx -t
systemctl enable --now nginx
systemctl reload nginx

echo "==> [Ubuntu] System installation complete!"
echo "Next step: Run 'deploy/ubuntu/deploy.sh' to sync code, create .env, and issue SSL certificates."
