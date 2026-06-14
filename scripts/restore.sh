#!/bin/bash
# Fortaleza Digital — restore script
# Usage: bash scripts/restore.sh <backup_file> [volume_name]
set -euo pipefail

if [ $# -lt 1 ]; then
    echo "Usage: $0 <backup_file.tar.gz[.enc]> [volume_name]"
    echo "  volume_name: chroma_data|audit_logs|documents|models|config (default: all)"
    exit 1
fi

BACKUP_FILE="$1"
TARGET_VOLUME="${2:-all}"
DECRYPTED=""

# Decrypt if .enc
if [[ "$BACKUP_FILE" == *.enc ]]; then
    if [ -z "${FORTALEZA_ENCRYPTION_KEY:-}" ]; then
        echo "ERROR: FORTALEZA_ENCRYPTION_KEY not set, cannot decrypt."
        exit 1
    fi
    echo "[fortaleza] Decrypting $BACKUP_FILE ..."
    DECRYPTED="${BACKUP_FILE%.enc}"
    python -c "
import sys; sys.path.insert(0, 'app')
from crypto import decrypt_file
decrypt_file('$BACKUP_FILE', '$DECRYPTED', master_key='$FORTALEZA_ENCRYPTION_KEY')
"
    BACKUP_FILE="$DECRYPTED"
fi

echo "[fortaleza] Restoring from $BACKUP_FILE ..."

if [ "$TARGET_VOLUME" = "all" ]; then
    tar -xzf "$BACKUP_FILE"
    echo "  ✓ Restored all volumes"
else
    tar -xzf "$BACKUP_FILE" "$TARGET_VOLUME"
    echo "  ✓ Restored $TARGET_VOLUME"
fi

# Clean up decrypted file
if [ -n "$DECRYPTED" ] && [ -f "$DECRYPTED" ]; then
    rm -f "$DECRYPTED"
fi

echo "[fortaleza] Restore complete."