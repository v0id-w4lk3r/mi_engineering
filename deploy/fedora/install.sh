#!/usr/bin/env bash
# ==============================================================================
# M.I. Engineering Works - Fedora Server Provisioning & Installation Script
# Supports: Fedora 38 / 39 / 40 / Server
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
if [[ "${ID:-}" != "fedora" && "${ID_LIKE:-}" != *"fedora"* ]]; then
    echo "ERROR: This installation script is designed for Fedora Server." >&2
    echo "Detected: ${PRETTY_NAME:-$ID}" >&2
    echo "For Ubuntu Server, please use deploy/ubuntu/install.sh instead." >&2
    exit 1
fi

echo "==> [Fedora] Starting system installation on ${PRETTY_NAME}..."

# 2. Package Installation via DNF
echo "==> [Fedora] Installing system packages via DNF..."
dnf install -y \
    python3 \
    python3-pip \
    python3-devel \
    gcc \
    git \
    nginx \
    certbot \
    python3-certbot-nginx \
    firewalld \
    policycoreutils-python-utils \
    curl \
    tar

# 3. Ensure uv is installed globally
if ! command -v uv >/dev/null 2>&1; then
    echo "==> [Fedora] Installing uv package manager..."
    curl -LsSf https://astral.sh/uv/install.sh | env UV_INSTALL_DIR="/usr/local/bin" sh
    chmod 755 /usr/local/bin/uv || true
else
    echo "==> [Fedora] uv is already installed at $(command -v uv)."
fi

# 4. User and Group Management (syn:webhost)
echo "==> [Fedora] Configuring application user and group..."
groupadd -f webhost

if ! id -u syn >/dev/null 2>&1; then
    useradd -m -g webhost -s /bin/bash syn
    echo "Created deployment user 'syn' in group 'webhost'."
else
    usermod -g webhost syn
fi

# Add Nginx user to webhost group so Nginx worker processes can read static/media
usermod -aG webhost nginx

# 5. Directory Layout Setup
echo "==> [Fedora] Creating production directory layout..."
mkdir -p /var/deployment/mi_engineering
mkdir -p /var/db
mkdir -p /var/data/media
mkdir -p /var/deployment/mi_engineering/staticfiles
mkdir -p /var/www/certbot

# Set ownership and base permissions
chown -R syn:webhost /var/deployment
chown -R syn:webhost /var/db
chown -R syn:webhost /var/data
chown -R nginx:nginx /var/www/certbot

chmod 750 /var/deployment
chmod 750 /var/deployment/mi_engineering
chmod 750 /var/db
chmod 775 /var/data/media
chmod g+s /var/data/media  # Newly uploaded files inherit webhost group
chmod 755 /var/www/certbot

# 6. SELinux Configuration
if command -v getenforce >/dev/null 2>&1 && [ "$(getenforce)" != "Disabled" ]; then
    echo "==> [Fedora] Configuring SELinux file contexts and booleans..."
    
    # Allow Nginx reverse proxy to loopback port 8000
    setsebool -P httpd_can_network_connect 1

    # Persistent file context for static files (read-only for Nginx)
    semanage fcontext -a -t httpd_sys_content_t "/var/deployment/mi_engineering/staticfiles(/.*)?" 2>/dev/null || \
    semanage fcontext -m -t httpd_sys_content_t "/var/deployment/mi_engineering/staticfiles(/.*)?" 2>/dev/null || true

    # Persistent file context for media files (read-only for Nginx)
    semanage fcontext -a -t httpd_sys_content_t "/var/data/media(/.*)?" 2>/dev/null || \
    semanage fcontext -m -t httpd_sys_content_t "/var/data/media(/.*)?" 2>/dev/null || true

    # Persistent file context for Certbot webroot challenge
    semanage fcontext -a -t httpd_sys_content_t "/var/www/certbot(/.*)?" 2>/dev/null || \
    semanage fcontext -m -t httpd_sys_content_t "/var/www/certbot(/.*)?" 2>/dev/null || true

    # Apply contexts
    restorecon -Rv /var/deployment/mi_engineering/staticfiles /var/data/media /var/www/certbot || true
else
    echo "==> [Fedora] SELinux is disabled or not present; skipping context configuration."
fi

# 7. Firewalld Configuration
echo "==> [Fedora] Configuring firewalld for HTTP and HTTPS..."
systemctl enable --now firewalld
firewall-cmd --permanent --add-service=http || true
firewall-cmd --permanent --add-service=https || true
firewall-cmd --reload || true

# 8. Systemd Service Installation
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "==> [Fedora] Installing systemd unit file..."
cp "$SCRIPT_DIR/mi_engineering.service" /etc/systemd/system/mi_engineering.service
chmod 644 /etc/systemd/system/mi_engineering.service
systemctl daemon-reload
systemctl enable mi_engineering.service

# 9. Nginx Bootstrap Setup (HTTP-only)
echo "==> [Fedora] Installing Nginx bootstrap configuration..."
cp "$SCRIPT_DIR/nginx.bootstrap.conf" /etc/nginx/conf.d/mi_engineering.conf

# Test and start Nginx
nginx -t
systemctl enable --now nginx
systemctl reload nginx

echo "==> [Fedora] System installation complete!"
echo "Next step: Run 'deploy/fedora/deploy.sh' to sync code, create .env, and issue SSL certificates."
