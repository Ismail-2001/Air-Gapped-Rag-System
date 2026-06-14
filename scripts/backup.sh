#!/bin/bash
# Fortaleza Digital — backup script
# Usage: bash scripts/backup.sh [--encrypt]
set -euo pipefail

BACKUP_DIR="${BACKUP_DIR:-./backups}"
RETENTION_DAYS="${RETENTION_DAYS:-30}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
ENCRYPT=${1:-}

mkdir -p "$BACKUP_DIR"

echo "[fortaleza] Starting backup $TIMESTAMP ..."

# ── Backup volumes ──
for volume in chroma_data audit_logs documents models; do
    src="./$volume"
    dst="$BACKUP_DIR/${volume}_${TIMESTAMP}.tar.gz"
    if [ -d "$src" ] && [ "$(ls -A "$src" 2>/dev/null)" ]; then
        tar -czf "$dst" -C . "$volume"
        echo "  ✓ Backed up $volume → $dst ($(du -h "$dst" | cut -f1))"

        # Encrypt if requested and key is set
        if [ "$ENCRYPT" = "--encrypt" ] && [ -n "${FORTALEZA_ENCRYPTION_KEY:-}" ]; then
            python -c "
import sys; sys.path.insert(0, 'app')
from crypto import encrypt_file
encrypt_file('$dst', master_key='$FORTALEZA_ENCRYPTION_KEY')
" && rm -f "$dst"
            echo "  ✓ Encrypted $volume backup"
        fi
    else
        echo "  - Skipping $volume (empty or missing)"
    fi
done

# ── Backup config files ──
CONFIG_BACKUP="$BACKUP_DIR/config_${TIMESTAMP}.tar.gz"
tar -czf "$CONFIG_BACKUP" \
    docker-compose.yml \
    .env 2>/dev/null || true
echo "  ✓ Backed up config → $CONFIG_BACKUP"

# ── Clean old backups ──
echo "[fortaleza] Cleaning backups older than $RETENTION_DAYS days..."
find "$BACKUP_DIR" -name "*.tar.gz" -type f -mtime +$RETENTION_DAYS -delete
find "$BACKUP_DIR" -name "*.tar.gz.enc" -type f -mtime +$RETENTION_DAYS -delete

echo "[fortaleza] Backup complete: $BACKUP_DIR/"
ls -lh "$BACKUP_DIR/" | tail -n +2