# Deployment Notes & Operations Guide

This guide details the complete deployment architecture, environment configuration, service setup, maintenance, and rollback steps for **M.I. Engineering Works** (`miengineeringworks.in`).

> [!TIP]
> Automated deployment scripts and distribution-specific runbooks for **Fedora Server** and **Ubuntu Server** are available under [`deploy/`](../deploy/README.md).

---

## 1. Architecture Overview

```text
                      ┌────────────────────────────────────────┐
                      │             Client / Browser           │
                      └──────────────────┬─────────────────────┘
                                         │ HTTPS (Port 443)
                                         ▼
                      ┌────────────────────────────────────────┐
                      │              Nginx (Reverse)           │
                      │  - Handles SSL Termination (Certbot)   │
                      │  - Static files: /staticfiles/         │
                      │  - Media files:  /media/               │
                      │  - Proxy: http://127.0.0.1:8000        │
                      └──────────────────┬─────────────────────┘
                                         │ HTTP (Loopback)
                                         ▼
                      ┌────────────────────────────────────────┐
                      │          Gunicorn (via systemd)        │
                      │  Unit: mi_engineering.service          │
                      │  Working Dir: /var/deployment/mi_engineering │
                      │  User: syn | Group: webhost            │
                      │  Entrypoint: ./entrypoint.sh            │
                      └──────────────────┬─────────────────────┘
                                         │
                                         ▼
                      ┌────────────────────────────────────────┐
                      │             Django Application         │
                      │  Settings: mi_engineering.settings.prod│
                      │  Database: SQLite in /var/db/db.sqlite3│
                      │  Media: /var/data/media/               │
                      └────────────────────────────────────────┘
```

---

## 2. Server Layout & Files

| Component | Path / Location | Description |
| :--- | :--- | :--- |
| **Project Root** | `/var/deployment/mi_engineering` | Deployment application codebase |
| **Static Files** | `/var/deployment/mi_engineering/staticfiles/` | Collected static files served by Nginx |
| **Media Files** | `/var/data/media/` | User uploaded images, RFQs & files |
| **Database** | `/var/db/db.sqlite3` | Production SQLite database file |
| **Environment File** | `/var/deployment/mi_engineering/.env` | Production environment configuration |
| **Systemd Service** | `/etc/systemd/system/mi_engineering.service` | Daemon unit file (`syn:webhost`) |
| **Nginx Config (Ubuntu)** | `/etc/nginx/sites-available/miengineeringworks.in.conf` | Symlinked to `sites-enabled/` |
| **Nginx Config (Fedora)** | `/etc/nginx/conf.d/mi_engineering.conf` | Fedora Nginx configuration |
| **SSL Certificates** | `/etc/letsencrypt/live/miengineeringworks.in/` | Let's Encrypt certificates managed by Certbot |

---

## 3. Environment Variables Reference (`.env`)

The production configuration reads variables loaded from `/var/deployment/mi_engineering/.env`:

| Key | Example / Default Value | Purpose |
| :--- | :--- | :--- |
| `ENV` | `prod` | Selects production mode |
| `DJANGO_SETTINGS_MODULE` | `mi_engineering.settings.prod` | Django settings module |
| `DJANGO_SECRET_KEY` | *(50+ char random string)* | Cryptographic signing key |
| `DEBUG` | `False` | Disables debug mode in production |
| `DJANGO_ALLOWED_HOSTS` | `miengineeringworks.in,www.miengineeringworks.in,127.0.0.1,localhost` | Host header validation |
| `CSRF_TRUSTED_ORIGINS` | `https://miengineeringworks.in,https://www.miengineeringworks.in` | Trusted origins for CSRF POST forms |
| `SECURE_SSL_REDIRECT` | `True` | Forces HTTPS redirects |
| `STATIC_ROOT` | `/var/deployment/mi_engineering/staticfiles` | Collected static files directory |
| `STATIC_URL` | `/static/` | Static URL prefix |
| `MEDIA_ROOT` | `/var/data/media` | Target directory for media uploads |
| `MEDIA_URL` | `/media/` | URL prefix for media assets |
| `DB_DIR` | `/var/db` | Directory where `db.sqlite3` is kept |
| `EMAIL_BACKEND` | `django.core.mail.backends.smtp.EmailBackend` | Mail backend |
| `EMAIL_HOST` | `smtp.gmail.com` | SMTP host |
| `EMAIL_PORT` | `587` | SMTP port |
| `EMAIL_USE_TLS` | `True` | Use TLS for mail connection |
| `EMAIL_HOST_USER` | `your-email@gmail.com` | SMTP account username |
| `EMAIL_HOST_PASSWORD` | *(App Password)* | Google App password |
| `DEFAULT_FROM_EMAIL` | `"M.I. Engineering Works" <your-email@gmail.com>` | Sender string |

---

## 4. Initial Setup & Installation Steps

### Step 1: User & Permissions Setup
Ensure the service user `syn` and group `webhost` exist and own required paths:
```bash
sudo groupadd -f webhost
sudo id -u syn &>/dev/null || sudo useradd -m -g webhost -s /bin/bash syn

# Add web server to webhost group:
# On Ubuntu:
sudo usermod -aG webhost www-data
# On Fedora:
sudo usermod -aG webhost nginx

sudo mkdir -p /var/deployment/mi_engineering /var/db /var/data/media /var/www/certbot
sudo chown -R syn:webhost /var/deployment /var/db /var/data
sudo chmod 750 /var/deployment /var/deployment/mi_engineering /var/db
sudo chmod 775 /var/data/media
sudo chmod g+s /var/data/media
```

### Step 2: Systemd Service Installation
```bash
sudo cp deployments/mi_engineering.service /etc/systemd/system/mi_engineering.service
sudo systemctl daemon-reload
sudo systemctl enable mi_engineering.service
```

### Step 3: Nginx & Certbot SSL
1. Install HTTP bootstrap configuration to allow ACME challenge:
   - On Ubuntu: `sudo cp deployments/miengineeringworks.in.bootstrap.conf /etc/nginx/sites-available/miengineeringworks.in.conf && sudo ln -sf /etc/nginx/sites-available/miengineeringworks.in.conf /etc/nginx/sites-enabled/`
   - On Fedora: `sudo cp deployments/miengineeringworks.in.bootstrap.conf /etc/nginx/conf.d/mi_engineering.conf`
2. Obtain certificate:
   ```bash
   sudo certbot certonly --webroot -w /var/www/certbot -d miengineeringworks.in -d www.miengineeringworks.in
   ```
3. Switch to production HTTPS configuration:
   - On Ubuntu: `sudo cp deployments/miengineeringworks.in.conf /etc/nginx/sites-available/miengineeringworks.in.conf`
   - On Fedora: `sudo cp deployments/miengineeringworks.in.conf /etc/nginx/conf.d/mi_engineering.conf`
   `sudo nginx -t && sudo systemctl reload nginx`

---

## 5. Routine Deployment & Updates Workflow

When pulling code updates or deploying a new release:

```bash
cd /var/deployment/mi_engineering

# 1. Pull latest code
git pull origin main

# 2. Update dependencies (using uv)
uv sync

# 3. Apply migrations & collectstatic
uv run python manage.py migrate --noinput
uv run python manage.py collectstatic --noinput -i "css/input.css"

# 4. Restart application service
sudo systemctl restart mi_engineering.service

# 5. Verify status
sudo systemctl status mi_engineering.service
```

---

## 6. Logs, Monitoring & Troubleshooting

### Systemd & Gunicorn Logs
```bash
sudo journalctl -u mi_engineering.service -f
sudo journalctl -u mi_engineering.service -n 100 --no-pager
```

### Nginx Logs
```bash
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log
```
