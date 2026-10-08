#!/usr/bin/env bash
# ==============================================================================
# M.I. Engineering Works - Fedora Routine Update Script
# Safely pulls code, updates dependencies, runs migrations, and reloads services.
# Can be executed by 'syn' (with sudo for systemctl) or by 'root'.
# ==============================================================================

set -Eeuo pipefail

TARGET_DIR="/var/deployment/mi_engineering"
BRANCH="${1:-main}"

echo "==> [Fedora Update] Starting routine update on branch '$BRANCH'..."

if [ ! -d "$TARGET_DIR" ]; then
    echo "ERROR: Target directory $TARGET_DIR does not exist." >&2
    exit 1
fi

cd "$TARGET_DIR"

# 1. Pull latest code from Git if it is a git repository
if [ -d ".git" ]; then
    echo "==> [Fedora Update] Pulling latest commits from git..."
    git fetch origin "$BRANCH"
    git checkout "$BRANCH"
    git pull origin "$BRANCH"
else
    echo "==> [Fedora Update] .git directory not found. Assuming code was pre-synchronized."
fi

# 2. Update Python dependencies using uv
echo "==> [Fedora Update] Updating dependencies with uv..."
if command -v uv >/dev/null 2>&1; then
    uv sync
elif [ -x "/usr/local/bin/uv" ]; then
    /usr/local/bin/uv sync
else
    echo "ERROR: uv package manager not found." >&2
    exit 1
fi

# 3. Apply database schema migrations
echo "==> [Fedora Update] Applying database migrations..."
if command -v uv >/dev/null 2>&1; then
    uv run python manage.py migrate --noinput
else
    /usr/local/bin/uv run python manage.py migrate --noinput
fi

# 4. Collect static files
echo "==> [Fedora Update] Collecting static files..."
if command -v uv >/dev/null 2>&1; then
    uv run python manage.py collectstatic --noinput -i "css/input.css"
else
    /usr/local/bin/uv run python manage.py collectstatic --noinput -i "css/input.css"
fi

# Ensure permissions
chmod -R u=rwX,go=rX "$TARGET_DIR/staticfiles" 2>/dev/null || true
chmod -R u=rwX,g=rwXs,o=rX /var/data/media 2>/dev/null || true

# 5. Restore SELinux contexts
if command -v restorecon >/dev/null 2>&1; then
    sudo restorecon -Rv "$TARGET_DIR/staticfiles" /var/data/media 2>/dev/null || true
fi

# 6. Validate Nginx configuration before restarting app
if command -v nginx >/dev/null 2>&1; then
    sudo nginx -t
fi

# 7. Restart application service
echo "==> [Fedora Update] Restarting mi_engineering.service..."
sudo systemctl restart mi_engineering.service

# 8. Verify service status
sleep 2
if sudo systemctl is-active --quiet mi_engineering.service; then
    echo "==> [Fedora Update] Service is active and running!"
else
    echo "ERROR: Service failed to start. Last log lines:" >&2
    sudo journalctl -u mi_engineering.service -n 25 --no-pager
    exit 1
fi

echo "==> [Fedora Update] Update finished successfully!"
