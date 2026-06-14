#!/bin/sh
# Provision self-signed TLS certificate for development.
# In production, replace with cert-manager / Let's Encrypt / PKI-issued certs.

set -e

SSL_DIR="${SSL_DIR:-/etc/nginx/ssl}"
CERT_FILE="${SSL_DIR}/cert.pem"
KEY_FILE="${SSL_DIR}/key.pem"
DAYS="${CERT_DAYS:-3650}"

if [ -f "$CERT_FILE" ] && [ -f "$KEY_FILE" ]; then
    echo "[fortaleza] TLS certificates already exist, skipping."
    exit 0
fi

mkdir -p "$SSL_DIR"

echo "[fortaleza] Generating self-signed TLS certificate (valid ${DAYS} days)..."
openssl req -x509 -nodes -days "$DAYS" -newkey rsa:4096 \
    -keyout "$KEY_FILE" \
    -out "$CERT_FILE" \
    -subj "/C=US/ST=Fortaleza/L=Fortaleza/O=Fortaleza Digital/OU=DevOps/CN=fortaleza.local" \
    -addext "subjectAltName=DNS:fortaleza.local,DNS:localhost,IP:127.0.0.1"

chmod 600 "$KEY_FILE"
chmod 644 "$CERT_FILE"

echo "[fortaleza] TLS certificate provisioned: $CERT_FILE"