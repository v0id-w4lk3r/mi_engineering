# Deployment Files

This directory contains the deployment configuration files for MI Engineering.

## Files

- [`miengineeringworks.in.conf`](file:///home/syn/code/work/mi_engineering/deployments/miengineeringworks.in.conf): Nginx reverse proxy and SSL configuration.
- [`mi_engineering.service`](file:///home/syn/code/work/mi_engineering/deployments/mi_engineering.service): Systemd service configuration for running Gunicorn via `entrypoint.sh`.

## Setup Instructions

### 1. Copy or Symlink Deployment Files to System Paths

To link or copy files to the system directories:

```bash
# Target deployment folder (if using /mnt/deployments/)
sudo mkdir -p /mnt/deployments
sudo cp -r deployments/* /mnt/deployments/

# Nginx configuration
sudo cp /mnt/deployments/miengineeringworks.in.conf /etc/nginx/sites-available/
sudo ln -sf /etc/nginx/sites-available/miengineeringworks.in.conf /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# Systemd service
sudo cp /mnt/deployments/mi_engineering.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now mi_engineering.service
```

### 2. Verify Service Status

```bash
sudo systemctl status mi_engineering.service
sudo journalctl -u mi_engineering.service -f
```
