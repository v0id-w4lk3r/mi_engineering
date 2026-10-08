# M.I. Engineering Works - Production Deployment System

Enterprise-ready, cross-distribution deployment suite supporting **Fedora Server** and **Ubuntu Server**.

---

## Supported Operating Systems

- **[Fedora Server Guide](fedora/README.md)**: Uses DNF, firewalld, SELinux enforcing mode, and systemd.
- **[Ubuntu Server Guide](ubuntu/README.md)**: Uses APT, UFW, AppArmor, and systemd.

---

## Directory & File Layout

```text
deploy/
├── README.md                  # This master deployment overview
├── TROUBLESHOOTING.md         # Cross-distribution diagnostics & recovery
├── SECURITY.md                # Security hardening, backups & rollback
├── fedora/
│   ├── install.sh             # DNF provisioning, SELinux, firewalld
│   ├── deploy.sh              # Initial deploy, secret key, SSL certbot
│   ├── update.sh              # Routine zero-downtime release update
│   ├── mi_engineering.service # Systemd unit configuration
│   ├── nginx.conf             # Production HTTPS Nginx configuration
│   ├── nginx.bootstrap.conf   # HTTP-only bootstrap configuration
│   └── README.md              # Fedora-specific installation guide
└── ubuntu/
    ├── install.sh             # APT provisioning, UFW, www-data permissions
    ├── deploy.sh              # Initial deploy, secret key, SSL certbot
    ├── update.sh              # Routine zero-downtime release update
    ├── mi_engineering.service # Systemd unit configuration
    ├── nginx.conf             # Production HTTPS Nginx configuration
    ├── nginx.bootstrap.conf   # HTTP-only bootstrap configuration
    └── README.md              # Ubuntu-specific installation guide
```

---

## Quick Start Cheat Sheet

### On Fedora Server:
```bash
# 1. Provision system packages & permissions
sudo bash deploy/fedora/install.sh

# 2. Deploy application and issue SSL certificates
sudo bash deploy/fedora/deploy.sh admin@miengineeringworks.in

# 3. Subsequent routine updates
sudo bash /var/deployment/mi_engineering/deploy/fedora/update.sh main
```

### On Ubuntu Server:
```bash
# 1. Provision system packages & permissions
sudo bash deploy/ubuntu/install.sh

# 2. Deploy application and issue SSL certificates
sudo bash deploy/ubuntu/deploy.sh admin@miengineeringworks.in

# 3. Subsequent routine updates
sudo bash /var/deployment/mi_engineering/deploy/ubuntu/update.sh main
```

---

## Key Production Parameters

- **Application Root**: `/var/deployment/mi_engineering`
- **Application User / Group**: `syn:webhost`
- **Database Directory**: `/var/db` (`db.sqlite3`)
- **Media Uploads Directory**: `/var/data/media`
- **Static Assets Directory**: `/var/deployment/mi_engineering/staticfiles`
- **Gunicorn Internal Bind**: `127.0.0.1:8000`
- **Domains**: `miengineeringworks.in`, `www.miengineeringworks.in`
