# Production Security & Operations Runbook

This document details security hardening, backup/restore procedures, rollback strategies, and operational safeguards for **M.I. Engineering Works**.

---

## 1. Security Architecture & Hardening

### Non-Root Execution
- The application process runs under the non-privileged service user `syn` and group `webhost`.
- Gunicorn binds strictly to loopback `127.0.0.1:8000`, preventing direct public access to Python application internals.

### Systemd Process Isolation
`mi_engineering.service` implements systemd sandbox directives:
- `ProtectSystem=full`: Mounts `/usr`, `/boot`, and `/etc` read-only for the service process.
- `ProtectHome=read-only`: Restricts write access to user home directories.
- `ReadWritePaths=/var/deployment/mi_engineering /var/db /var/data/media`: Whitelists only the directories strictly required for SQLite, uploads, and assets.
- `NoNewPrivileges=true`: Prevents execution of binaries with suid/guid privilege escalation.
- `PrivateTmp=true`: Isolates temporary directory namespaces.

### File Permissions & Access Control
- `.env` files are restricted to `chmod 600` and owned by `syn:webhost`.
- SQLite database directory `/var/db` is restricted to `chmod 750` with no public web server exposure.
- Static assets `/var/deployment/mi_engineering/staticfiles` are read-only for Nginx (`chmod -R u=rwX,go=rX`).
- Uploaded media `/var/data/media` has the `setgid` bit set (`chmod g+s`) with `umask 0002` so new files inherit group `webhost` and cannot execute code.

### Nginx Defense in Depth
- Public requests to hidden files (`.env`, `.git`, `.gitignore`) are blocked:
  ```nginx
  location ~ /\. {
      deny all;
      access_log off;
      log_not_found off;
  }
  ```
- Public requests to SQLite database files are blocked:
  ```nginx
  location ~* \.(sqlite3|db)$ {
      deny all;
  }
  ```
- Security headers enabled:
  - `X-Content-Type-Options: nosniff`
  - `X-Frame-Options: SAMEORIGIN`
  - `X-XSS-Protection: 1; mode=block`
  - `Referrer-Policy: strict-origin-when-cross-origin`
- Maximum upload limit set to `25M` (`client_max_body_size 25M`).

---

## 2. Backup & Restore Procedures

### Database Backup (SQLite)
Because SQLite databases are single files, take consistent atomic backups:

#### Backup Command:
```bash
#!/usr/bin/env bash
BACKUP_DIR="/var/backups/mi_engineering/db"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
mkdir -p "$BACKUP_DIR"

# Perform SQLite online backup
sqlite3 /var/db/db.sqlite3 ".backup '$BACKUP_DIR/db_$TIMESTAMP.sqlite3'"
gzip "$BACKUP_DIR/db_$TIMESTAMP.sqlite3"
chmod 600 "$BACKUP_DIR/db_$TIMESTAMP.sqlite3.gz"

# Retain backups for 30 days
find "$BACKUP_DIR" -type f -name "db_*.sqlite3.gz" -mtime +30 -delete
```

#### Restore Command:
```bash
# 1. Stop application service
sudo systemctl stop mi_engineering.service

# 2. Decompress and restore database
gunzip -c /var/backups/mi_engineering/db/db_YYYYMMDD_HHMMSS.sqlite3.gz > /var/db/db.sqlite3
sudo chown syn:webhost /var/db/db.sqlite3
sudo chmod 660 /var/db/db.sqlite3

# 3. Start service
sudo systemctl start mi_engineering.service
```

---

### Media Files Backup
```bash
BACKUP_DIR="/var/backups/mi_engineering/media"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
mkdir -p "$BACKUP_DIR"

tar -czf "$BACKUP_DIR/media_$TIMESTAMP.tar.gz" -C /var/data media
chmod 600 "$BACKUP_DIR/media_$TIMESTAMP.tar.gz"
```

---

## 3. Deployment Rollback Strategy

In the event an application release introduces a critical bug:

### Automated Rollback Steps
```bash
cd /var/deployment/mi_engineering

# 1. Revert Git commit to previous known good state
git reset --hard HEAD~1

# 2. Re-sync dependencies
uv sync

# 3. If migrations need rolling back, revert specific app migration:
# uv run python manage.py migrate <app_name> <migration_number>

# 4. Re-collect static assets
uv run python manage.py collectstatic --noinput -i "css/input.css"

# 5. Restart application
sudo systemctl restart mi_engineering.service

# 6. Verify health
curl -Iv https://miengineeringworks.in
```

---

## 4. Firewall & Network Exposure

Only necessary ports are opened to external traffic:
- Port 80 (HTTP) -> Redirects to HTTPS
- Port 443 (HTTPS) -> TLS reverse proxy
- Port 22 (SSH) -> System administration (key-based auth recommended)

All other ports (including internal Gunicorn port 8000) are blocked by the firewall.
