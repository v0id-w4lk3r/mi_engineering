# Ubuntu Server Production Deployment Guide

Complete, step-by-step production deployment instructions for **M.I. Engineering Works** on **Ubuntu Server** (Ubuntu 22.04 LTS / 24.04 LTS).

---

## 1. Architecture Summary

| Component | Path / Configuration | Description |
| :--- | :--- | :--- |
| **Operating System** | Ubuntu Server LTS (x86_64) | Tested on 22.04 and 24.04 LTS |
| **Application Root** | `/var/deployment/mi_engineering` | Django codebase & virtual environment |
| **Static Files** | `/var/deployment/mi_engineering/staticfiles` | Served directly by Nginx |
| **Media Files** | `/var/data/media` | User uploaded PDFs, images, RFQs |
| **Database** | `/var/db/db.sqlite3` | SQLite production database |
| **ACME Webroot** | `/var/www/certbot` | Let's Encrypt validation |
| **Service Identity** | `syn:webhost` | Non-root system execution user/group |
| **Web Server User** | `www-data` (added to `webhost`) | Reverse proxy with read access |
| **Systemd Service** | `/etc/systemd/system/mi_engineering.service` | Managed Gunicorn process |
| **Nginx Config** | `/etc/nginx/sites-available/miengineeringworks.in.conf` | Symlinked to `sites-enabled` |
| **Firewall** | `UFW` (ports 80, 443, 22) | Managed via ufw |

---

## 2. Automated Installation & Deployment

### Step 1: Clone Repository
On your fresh Ubuntu Server, clone the repository:
```bash
sudo apt-get update && sudo apt-get install -y git
git clone https://github.com/your-org/mi_engineering.git /tmp/mi_engineering_repo
cd /tmp/mi_engineering_repo
```

### Step 2: Run Initial System Provisioning
Execute the automated Ubuntu provisioning script:
```bash
sudo bash deploy/ubuntu/install.sh
```

This installs APT packages, installs `uv`, creates user `syn` and group `webhost`, adds `www-data` to `webhost`, configures UFW firewall, removes default Nginx site, and enables the bootstrap Nginx configuration.

### Step 3: Run Full Initial Deployment
```bash
sudo bash deploy/ubuntu/deploy.sh admin@miengineeringworks.in
```

This synchronizes the codebase into `/var/deployment/mi_engineering`, generates a cryptographically secure `.env`, syncs Python dependencies with `uv`, runs database migrations, collects static assets, starts `mi_engineering.service`, issues Let's Encrypt SSL certificates via Certbot, and reloads Nginx with production HTTPS.

---

## 3. Manual Step-by-Step Installation (Alternative)

If you prefer executing commands manually instead of running the scripts:

### 1. Install System Packages
```bash
sudo apt-get update
sudo apt-get install -y \
    python3 python3-pip python3-venv python3-dev build-essential \
    git nginx certbot python3-certbot-nginx ufw curl tar rsync

# Install uv globally
curl -LsSf https://astral.sh/uv/install.sh | sudo env UV_INSTALL_DIR="/usr/local/bin" sh
sudo chmod 755 /usr/local/bin/uv
```

### 2. User & Directory Setup
```bash
sudo groupadd -f webhost
sudo id -u syn &>/dev/null || sudo useradd -m -g webhost -s /bin/bash syn
sudo usermod -aG webhost www-data

sudo mkdir -p /var/deployment/mi_engineering
sudo mkdir -p /var/db
sudo mkdir -p /var/data/media
sudo mkdir -p /var/deployment/mi_engineering/staticfiles
sudo mkdir -p /var/www/certbot

sudo chown -R syn:webhost /var/deployment /var/db /var/data
sudo chown -R www-data:www-data /var/www/certbot

sudo chmod 750 /var/deployment /var/deployment/mi_engineering /var/db
sudo chmod 775 /var/data/media
sudo chmod g+s /var/data/media
sudo chmod 755 /var/www/certbot
```

### 3. Firewall (UFW)
```bash
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

### 4. Clone Code & Environment Configuration
```bash
sudo cp -r . /var/deployment/mi_engineering/
sudo chown -R syn:webhost /var/deployment/mi_engineering

# Create .env
cd /var/deployment/mi_engineering
sudo cp .env.example .env
sudo chown syn:webhost .env
sudo chmod 600 .env

# Generate secret key in .env
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(50))")
sudo sed -i "s|^DJANGO_SECRET_KEY=.*|DJANGO_SECRET_KEY=${SECRET_KEY}|" .env
```

### 5. Install Dependencies & Build Assets
```bash
# Sync dependencies with uv as user syn
sudo -u syn -H /usr/local/bin/uv sync

# Run migrations and static collection
sudo -u syn -H /usr/local/bin/uv run python manage.py migrate --noinput
sudo -u syn -H /usr/local/bin/uv run python manage.py collectstatic --noinput -i "css/input.css"

# Re-apply permissions
sudo chmod -R u=rwX,go=rX /var/deployment/mi_engineering/staticfiles
```

### 6. Install Services & Nginx Bootstrap
```bash
# Install systemd service
sudo cp deploy/ubuntu/mi_engineering.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now mi_engineering.service

# Remove default site to prevent domain conflict
sudo rm -f /etc/nginx/sites-enabled/default

# Install Bootstrap Nginx (HTTP-only)
sudo cp deploy/ubuntu/nginx.bootstrap.conf /etc/nginx/sites-available/miengineeringworks.in.conf
sudo ln -sf /etc/nginx/sites-available/miengineeringworks.in.conf /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl enable --now nginx
```

### 7. Obtain SSL Certificates & Enable HTTPS
```bash
sudo certbot certonly --webroot -w /var/www/certbot \
    -d miengineeringworks.in -d www.miengineeringworks.in \
    --agree-tos -m admin@miengineeringworks.in

# Switch to production HTTPS configuration
sudo cp deploy/ubuntu/nginx.conf /etc/nginx/sites-available/miengineeringworks.in.conf
sudo ln -sf /etc/nginx/sites-available/miengineeringworks.in.conf /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## 4. Routine Release / Update Workflow

Whenever updates are pushed to git:
```bash
sudo bash /var/deployment/mi_engineering/deploy/ubuntu/update.sh main
```

Or manually:
```bash
cd /var/deployment/mi_engineering
git pull origin main
uv sync
uv run python manage.py migrate --noinput
uv run python manage.py collectstatic --noinput -i "css/input.css"
sudo systemctl restart mi_engineering.service
```

---

## 5. Ubuntu Troubleshooting

### 1. Default Nginx Welcome Page Displayed
If Nginx serves the Ubuntu welcome page instead of the application:
```bash
sudo rm -f /etc/nginx/sites-enabled/default
sudo systemctl reload nginx
```

### 2. Gunicorn Fails: `217/USER`
Ensure user `syn` and group `webhost` exist on the system:
```bash
id syn
# If missing:
sudo groupadd -f webhost
sudo useradd -m -g webhost -s /bin/bash syn
```

### 3. Nginx 403 Forbidden on Media / Static Files
Ensure `www-data` is part of the `webhost` group:
```bash
groups www-data
# If webhost is not listed:
sudo usermod -aG webhost www-data
sudo systemctl restart nginx
```

### 4. Viewing Logs
```bash
# Stream Django / Gunicorn logs
sudo journalctl -u mi_engineering.service -f

# View Nginx access & error logs
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log
```
