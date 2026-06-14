#!/bin/bash
set -euo pipefail

SECRETS_DIR=".secrets"
mkdir -p "$SECRETS_DIR"

openssl rand -hex 64 > "$SECRETS_DIR/jwt_secret.txt"
openssl rand -hex 32 > "$SECRETS_DIR/encryption_key.txt"
openssl rand -hex 64 > "$SECRETS_DIR/audit_hmac_key.txt"
openssl rand -hex 32 > "$SECRETS_DIR/db_password.txt"

chmod 600 "$SECRETS_DIR"/*.txt
echo "[FORTALEZA] Secrets generated in $SECRETS_DIR"
