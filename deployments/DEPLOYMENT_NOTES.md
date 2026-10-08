# Deployment Notes & Operations Guide

This guide details the complete deployment architecture, environment configuration, service setup, maintenance, and rollback steps for **M.I. Engineering Works** (`miengineeringworks.in`).

---

## 1. Architecture Overview

```
                      ┌────────────────────────────────────────┐
                      │             Client / Browser           │
                      └──────────────────┬─────────────────────┘
                                         │ HTTPS (Port 443)
                                         ▼
                      ┌────────────────────────────────────────┐
                      │              Nginx (Reverse)           │
                      │  - Handles SSL Termination (Certbot)   │
                      │  - Static files: /staticfiles/         │
                      │  - Proxy: http://127.0.0.1:8000        │
                      └──────────────────┬─────────────────────┘
                                         │ HTTP
                                         ▼
                      ┌────────────────────────────────────────┐
                      │          Gunicorn (via systemd)        │
                      │  Unit: mi_engineering.service          │
                      │  Working Dir: /var/webhost/mi_engineering│
                      │  Entrypoint: ./entrypoint.sh            │
                      └──────────────────┬─────────────────────┘
                                         │
                                         ▼
                      ┌────────────────────────────────────────┐
                      │             Django Application         │
                      │  Settings: mi_engineering.settings.prod│
                      │  Database: SQLite in data/db.sqlite3   │
                      │  Media: media/                         │
                      └────────────────────────────────────────┘
```

---

## 2. Server Layout & Files

| Component | Path / Location | Description |
| :--- | :--- | :--- |
| **Project Root** | `/var/webhost/mi_engineering` | Deployment application codebase |
| **Deployments Backup** | `/mnt/deployments/` | Backup / staging directory for configs |
| **Nginx Config** | `/etc/nginx/sites-available/miengineeringworks.in.conf` | VirtualHost config |
| **Nginx Enabled** | `/etc/nginx/sites-enabled/miengineeringworks.in.conf` | Symlink to sites-available |
| **Systemd Service** | `/etc/systemd/system/mi_engineering.service` | Daemon unit file |
| **Static Files** | `/var/webhost/mi_engineering/staticfiles/` | Collected static files served by Nginx |
| **Media Files** | `/var/webhost/mi_engineering/media/` | User uploaded images & files |
| **Database** | `/var/webhost/mi_engineering/data/db.sqlite3` | Production SQLite database file |
| **SSL Certificates** | `/etc/letsencrypt/live/miengineeringworks.in/` | Let's Encrypt certificates managed by Certbot |

---

## 3. Environment Variables Reference (`.env`)

The production configuration reads variables loaded from `/var/webhost/mi_engineering/.env`:

| Key | Example / Default Value | Purpose |
| :--- | :--- | :--- |
| `ENV` | `prod` | Selects `mi_engineering.settings.prod` |
| `DJANGO_SECRET_KEY` | *(50+ char random string)* | Cryptographic signing key |
| `DEBUG` | `False` | Disables debug mode in production |
| `ALLOWED_HOSTS` | `miengineeringworks.in,www.miengineeringworks.in,localhost,127.0.0.1` | Host header validation |
| `CSRF_TRUSTED_ORIGINS` | `https://miengineeringworks.in,https://www.miengineeringworks.in` | Trusted origins for CSRF POST forms |
| `SECURE_SSL_REDIRECT` | `True` | Forces HTTPS redirects |
| `DB_DIR` | `/var/webhost/mi_engineering/data` | Directory where `db.sqlite3` is kept |
| `MEDIA_ROOT` | `/var/webhost/mi_engineering/media` | Target directory for media uploads |
| `MEDIA_URL` | `/media/` | URL prefix for media assets |
| `EMAIL_BACKEND` | `django.core.mail.backends.smtp.EmailBackend` | Mail backend |
| `EMAIL_HOST` | `smtp.gmail.com` | SMTP host |
| `EMAIL_PORT` | `587` | SMTP port |
| `EMAIL_USE_TLS` | `True` | Use TLS for mail connection |
| `EMAIL_HOST_USER` | `miengineering17@gmail.com` | SMTP account username |
| `EMAIL_HOST_PASSWORD` | *(App Password)* | Google App password |
| `DEFAULT_FROM_EMAIL` | `"M.I. Engineering Works" <miengineering17@gmail.com>` | Sender string |

---

## 4. Initial Setup & Installation Steps

### Step 1: User & Permissions Setup
Ensure the deployment user `syn` and webhost group exist:
```bash
sudo groupadd -f webhost
sudo usermod -aG webhost syn
sudo chown -R syn:webhost /var/webhost/mi_engineering
```

### Step 2: Sync Deployment Configs
```bash
# Backup/Store configs in /mnt/deployments
sudo mkdir -p /mnt/deployments
sudo cp -r /var/webhost/mi_engineering/deployments/* /mnt/deployments/

# Copy systemd unit file
sudo cp /mnt/deployments/mi_engineering.service /etc/systemd/system/mi_engineering.service
sudo systemctl daemon-reload

# Copy Nginx server block
sudo cp /mnt/deployments/miengineeringworks.in.conf /etc/nginx/sites-available/miengineeringworks.in.conf
sudo ln -sf /etc/nginx/sites-available/miengineeringworks.in.conf /etc/nginx/sites-enabled/
```

### Step 3: SSL Certificate (Certbot)
If SSL certificates are not yet obtained:
```bash
sudo certbot --nginx -d miengineeringworks.in -d www.miengineeringworks.in
```

### Step 4: Validate and Reload Nginx
```bash
sudo nginx -t
sudo systemctl reload nginx
```

### Step 5: Enable & Start Application Service
```bash
sudo systemctl enable mi_engineering.service
sudo systemctl restart mi_engineering.service
```

---

## 5. Routine Deployment & Updates Workflow

When pulling code updates or deploying a new release:

```bash
cd /var/webhost/mi_engineering

# 1. Pull latest code
git pull origin main

# 2. Update dependencies (using uv)
uv sync

# 3. Restart application service (entrypoint.sh will run check, makemigrations, migrate, and collectstatic)
sudo systemctl restart mi_engineering.service

# 4. Verify status
sudo systemctl status mi_engineering.service
```

---

## 6. Logs, Monitoring & Troubleshooting

### Systemd & Gunicorn Logs
```bash
# Stream live logs
sudo journalctl -u mi_engineering.service -f

# View last 100 log lines
sudo journalctl -u mi_engineering.service -n 100 --no-pager
```

### Nginx Logs
```bash
# Nginx error log
sudo tail -f /var/log/nginx/error.log

# Nginx access log
sudo tail -f /var/log/nginx/access.log
```

### Common Issues
1. **502 Bad Gateway**:
   - Check if the Gunicorn service is running: `sudo systemctl status mi_engineering.service`
   - Check if port 8000 is open: `ss -tulpn | grep 8000`
2. **Static files 404 or 403 Forbidden**:
   - Verify permissions on `/var/webhost/mi_engineering/staticfiles/` (`chmod 755` for directories, `chmod 644` for files).
   - Ensure Nginx worker user (`nginx` or `www-data`) has read permissions through all parent directories.
3. **Database locked (SQLite)**:
   - Make sure only the Gunicorn workers are writing to the database file.
   - `prod.py` has an SQLite timeout set to 20 seconds.
