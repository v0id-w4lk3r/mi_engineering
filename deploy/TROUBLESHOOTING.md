# Production Troubleshooting Guide

Comprehensive solutions for common production issues on **Fedora Server** and **Ubuntu Server**.

---

## 1. Gunicorn & Systemd Service Failures

### Symptom: `systemctl status mi_engineering.service` shows `status=217/USER`
**Cause:** The user `syn` or group `webhost` specified in the systemd unit file does not exist on the Linux system.
**Resolution:**
```bash
# Check if user and group exist
id syn

# Create group and user if missing
sudo groupadd -f webhost
sudo id -u syn &>/dev/null || sudo useradd -m -g webhost -s /bin/bash syn
sudo systemctl restart mi_engineering.service
```

---

### Symptom: `uv: command not found` in Systemd Journal
**Cause:** `uv` was installed in a user's interactive shell path (`~/.cargo/bin`) rather than a system-wide PATH accessible to systemd.
**Resolution:**
1. Install `uv` globally to `/usr/local/bin`:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sudo env UV_INSTALL_DIR="/usr/local/bin" sh
   sudo chmod 755 /usr/local/bin/uv
   ```
2. Verify `deploy/<distro>/mi_engineering.service` includes `/usr/local/bin` in `Environment="PATH=..."`.
3. The project's `entrypoint.sh` includes fallback detection to run `.venv/bin/gunicorn` and `.venv/bin/python` directly even if `uv` is not present in PATH.

---

### Symptom: 502 Bad Gateway from Nginx
**Cause:** Gunicorn is either not running, crashed on startup, or Nginx is blocked from connecting to `127.0.0.1:8000`.
**Resolution:**
1. Check if Gunicorn is listening on port 8000:
   ```bash
   sudo ss -tulpn | grep 8000
   ```
2. Check Gunicorn startup errors in journal:
   ```bash
   sudo journalctl -u mi_engineering.service -n 50 --no-pager
   ```
3. On Fedora, check SELinux network connect boolean:
   ```bash
   sudo getsebool httpd_can_network_connect
   # If 'off', enable it permanently:
   sudo setsebool -P httpd_can_network_connect 1
   ```

---

## 2. Static & Media File Issues

### Symptom: CSS/JS returning 404 Not Found
**Cause:** `collectstatic` was not run, or Nginx `alias` does not match `STATIC_ROOT`.
**Resolution:**
1. Verify static files are collected:
   ```bash
   ls -la /var/deployment/mi_engineering/staticfiles
   ```
2. If empty, run `collectstatic`:
   ```bash
   cd /var/deployment/mi_engineering
   sudo -u syn /usr/local/bin/uv run python manage.py collectstatic --noinput -i "css/input.css"
   ```
3. Ensure Nginx configuration has the trailing slash on the alias:
   ```nginx
   location /static/ {
       alias /var/deployment/mi_engineering/staticfiles/;
   }
   ```

---

### Symptom: CSS or Images returning 403 Forbidden
**Cause:** Nginx worker process cannot read the directory or traverse parent directories.
**Resolution:**
1. Verify directory traversal permissions on parents:
   ```bash
   sudo chmod 755 /var
   sudo chmod 755 /var/deployment
   sudo chmod 750 /var/deployment/mi_engineering
   sudo chmod -R u=rwX,go=rX /var/deployment/mi_engineering/staticfiles
   ```
2. On Fedora, verify `nginx` is in the `webhost` group:
   ```bash
   sudo usermod -aG webhost nginx
   ```
3. On Ubuntu, verify `www-data` is in the `webhost` group:
   ```bash
   sudo usermod -aG webhost www-data
   ```

---

### Symptom: SELinux Denials on Fedora (`AVC: denied { getattr / read }`)
**Cause:** Files were copied without the correct SELinux context (`httpd_sys_content_t`).
**Resolution:**
1. Check audit log for denials:
   ```bash
   sudo ausearch -m avc -ts recent
   ```
2. Re-label static and media directories:
   ```bash
   sudo semanage fcontext -a -t httpd_sys_content_t "/var/deployment/mi_engineering/staticfiles(/.*)?" 2>/dev/null || true
   sudo semanage fcontext -a -t httpd_sys_content_t "/var/data/media(/.*)?" 2>/dev/null || true
   sudo restorecon -Rv /var/deployment/mi_engineering/staticfiles /var/data/media
   ```

---

### Symptom: Newly Uploaded Media Files Return 403 Forbidden
**Cause:** The application created files without read permissions for the web server group.
**Resolution:**
1. The project sets `UMask=0002` in `mi_engineering.service` and `entrypoint.sh`.
2. Ensure the media folder has the `setgid` bit enabled so new files inherit group `webhost`:
   ```bash
   sudo chown -R syn:webhost /var/data/media
   sudo chmod -R 775 /var/data/media
   sudo chmod g+s /var/data/media
   ```

---

## 3. Nginx & Domain Configuration

### Symptom: Conflicting or Duplicate Server Name Warnings
**Cause:** Another virtual host is defining the same `server_name` or default host.
**Resolution:**
1. On Ubuntu, remove the default site:
   ```bash
   sudo rm -f /etc/nginx/sites-enabled/default
   ```
2. Search for duplicate server names across Nginx configurations:
   ```bash
   grep -rn "server_name" /etc/nginx/
   ```
3. Test syntax:
   ```bash
   sudo nginx -t
   sudo systemctl reload nginx
   ```

---

### Symptom: Infinite Redirect Loop on HTTPS
**Cause:** Django is attempting to redirect to HTTPS while Nginx does not forward `X-Forwarded-Proto`.
**Resolution:**
1. In `miengineeringworks.in.conf`, ensure the proxy location includes:
   ```nginx
   proxy_set_header X-Forwarded-Proto $scheme;
   ```
2. In `mi_engineering/settings/prod.py`, verify:
   ```python
   SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
   ```
3. If Nginx already redirects port 80 to 443 with `return 301 https://$host$request_uri;`, you can set `SECURE_SSL_REDIRECT=False` in `.env` to prevent redundant redirects.

---

## 4. Certbot & Let's Encrypt Failures

### Symptom: Nginx Fails to Start with `cannot load certificate ... fullchain.pem: No such file`
**Cause:** Production HTTPS config was activated before the certificates were issued.
**Resolution:**
1. Temporarily activate the bootstrap configuration:
   - On Fedora:
     ```bash
     sudo cp deploy/fedora/nginx.bootstrap.conf /etc/nginx/conf.d/mi_engineering.conf
     sudo systemctl reload nginx
     ```
   - On Ubuntu:
     ```bash
     sudo cp deploy/ubuntu/nginx.bootstrap.conf /etc/nginx/sites-available/miengineeringworks.in.conf
     sudo systemctl reload nginx
     ```
2. Request the certificate via webroot:
   ```bash
   sudo certbot certonly --webroot -w /var/www/certbot \
       -d miengineeringworks.in -d www.miengineeringworks.in \
       --agree-tos -m admin@miengineeringworks.in
   ```
3. Once certificates exist, re-apply the production HTTPS configuration.

---

## 5. Django Environment & Secret Validation

### Symptom: `ImproperlyConfigured: DJANGO_SECRET_KEY environment variable is required`
**Cause:** `.env` is missing or `DJANGO_SECRET_KEY` is not defined.
**Resolution:**
1. Create `/var/deployment/mi_engineering/.env`:
   ```bash
   cp /var/deployment/mi_engineering/.env.example /var/deployment/mi_engineering/.env
   ```
2. Generate a key:
   ```bash
   python3 -c "import secrets; print('DJANGO_SECRET_KEY=' + secrets.token_urlsafe(50))" >> /var/deployment/mi_engineering/.env
   sudo chmod 600 /var/deployment/mi_engineering/.env
   sudo chown syn:webhost /var/deployment/mi_engineering/.env
   sudo systemctl restart mi_engineering.service
   ```
