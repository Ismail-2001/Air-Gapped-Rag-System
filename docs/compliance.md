# Fortaleza Digital — Compliance & Controls

## 1. Data Protection (Encryption at Rest & in Transit)

| Control | Implementation | Standard |
|---------|---------------|----------|
| **At-rest encryption** | AES-256-GCM via `app/crypto.py` using PBKDF2-derived keys (600K iterations, SHA-512) | NIST SP 800-38D |
| **In-transit encryption** | TLS 1.3 only via nginx reverse proxy; ciphers: `TLS_AES_256_GCM_SHA384`, `TLS_CHACHA20_POLY1305_SHA256` | NIST SP 800-52 Rev. 2 |
| **Certificate management** | Self-signed for dev; production should use cert-manager + Let's Encrypt or PKI | — |
| **Key derivation** | PBKDF2-HMAC-SHA512, 600,000 iterations, random 16-byte salt | OWASP ASVS v4.0.3 |

## 2. Access Control

| Control | Implementation |
|---------|---------------|
| **Authentication** | JWT-based with PBKDF2 password hashing (`app/auth.py`) |
| **RBAC roles** | 7 tiers: `viewer`, `analyst`, `ingestor`, `operator`, `auditor`, `admin`, `superadmin` |
| **Clearance levels** | Integer 1–7; each role has a minimum clearance requirement |
| **Password storage** | PBKDF2-HMAC-SHA256, 32-byte salt, variable iterations (scoped by `FORTALEZA_AUTH_MODE`) |
| **Rate limiting** | Per-user sliding window, configurable max requests per window (`app/rate_limiter.py`) |

## 3. Audit & Accountability

| Control | Implementation | Standard |
|---------|---------------|----------|
| **Event logging** | Structured JSON logging to file (`app/logging_config.py`) | SOC 2 CC3, CC5 |
| **Immutability** | HMAC-SHA256 chained audit log; tamper detection via chain integrity verification (`app/audit.py`) | NIST SP 800-53 AU-3, AU-6 |
| **Event categories** | Login, logout, query execution, document ingestion, database purge, error events | — |
| **User attribution** | Each audit event includes `user_id`, `ip_address`, `session_id`, and `resource` | PCI DSS 10.2 |
| **Retention** | Audit logs stored in Docker volume `audit_logs`; backup with `scripts/backup.sh` | — |

## 4. Network Security

| Control | Implementation |
|---------|---------------|
| **Network isolation** | Docker `internal: true` bridge network — no egress allowed outside the compose stack |
| **K8s isolation** | `NetworkPolicy` (`airgap-isolation`) restricts ingress/egress to pod-local ports only |
| **Service exposure** | Only nginx port 443 exposed; all internal services (app:8501, ollama:11434) are reachable only within the Docker / K8s network |
| **TLS termination** | nginx reverse proxy on port 443; HTTP (80) redirects to HTTPS; HSTS enabled |

## 5. Input Sanitization & Injection Defense

| Control | Implementation |
|---------|---------------|
| **Prompt injection** | 40+ regex patterns blocking DAN, jailbreak, Unicode obfuscation, multilingual injections (`app/prompt_shield.py`) |
| **Query validation** | `app/input_validator.py` blocks SQL injection, shell injection, system prompt overrides |
| **Content sanitization** | Every document chunk is sanitized before being used as context via `sanitize_text()` |
| **Context delimitation** | Documents wrapped in `[CHUNK_START]` / `[CHUNK_END]` markers; LLM instructed to treat documents as data, not instructions |

## 6. Supply Chain & Build Security

| Control | Implementation |
|---------|---------------|
| **Base image pinning** | All Docker base images pinned to specific SHA256 digests; no `:latest` tags |
| **Vulnerability scanning** | Trivy scans every build for CRITICAL/HIGH CVEs (`security-scan.yml`) |
| **Dependency auditing** | `pip-audit` and `safety` run in CI on every push |
| **Secret scanning** | Gitleaks scans repository history for leaked credentials |
| **License compliance** | Automated license check in CI (rejects GPL/AGPL dependencies) |
| **Pre-commit hooks** | Ruff, mypy, bandit, detect-secrets run before every commit |

## 7. Backup & Disaster Recovery

| Control | Implementation |
|---------|---------------|
| **Volume backup** | `scripts/backup.sh` — timestamped tarballs of chroma_data, audit_logs, documents, models |
| **Optional encryption** | Backup files encrypted with AES-256-GCM when `FORTALEZA_ENCRYPTION_KEY` is set |
| **Restore procedure** | `scripts/restore.sh <backup_file> [volume]` — supports `.enc` files |
| **Retention** | Automatic cleanup of backups older than 30 days (configurable via `RETENTION_DAYS`) |

## 8. Air-Gap Compliance

| Requirement | Verification |
|-------------|-------------|
| No external DNS resolution | All containers on `internal: true` network |
| No egress at runtime | Verified by `test_airgap.py` — attempts to resolve `google.com` must fail |
| All models pre-cached | Llama 3 is downloaded during Docker build (`ollama/Dockerfile`) |
| All Python packages pre-cached | Transitive deps are downloaded during image build; `TRANSFORMERS_OFFLINE=1`, `HF_HUB_OFFLINE=1` enforced |
| No telemetry | `ANONYMIZED_TELEMETRY=false`, `DO_NOT_TRACK=1`, `CHROMADB_TELEMETRY=false` |
| No license restrictions | 100% MIT / Apache 2.0 dependencies — no GPL / AGPL |

## 9. Incident Response (IR) Procedures

1. **Detection**: Monitor structured logs (`audit_logs/`), Prometheus metrics (`/metrics` on port 8000), and system health endpoints (`/health`)
2. **Containment**: Revoke JWT tokens via secret rotation; adjust RBAC roles if compromise is suspected
3. **Investigation**: Use the audit chain integrity verification (`GET /audit/verify`) to detect tampering; cross-reference with structured logs
4. **Recovery**: Restore from encrypted backup (`scripts/restore.sh`); rotate all secrets (`FORTALEZA_JWT_SECRET`, `FORTALEZA_ENCRYPTION_KEY`, admin password)
5. **Post-mortem**: Review audit events, Prometheus metrics, and container logs to determine root cause; update controls and documentation

## 10. Standards Mapping

| Framework | Controls Covered |
|-----------|-----------------|
| **SOC 2** (CC1–CC9) | CC3 (audit), CC5 (monitoring), CC6 (access), CC7 (incident response) |
| **NIST SP 800-53** | AC-2 (account mgmt), AU-3 (audit), AU-6 (review), SC-8 (transmission), SC-28 (at-rest) |
| **PCI DSS v4.0** | 7.2 (access), 8.3 (authentication), 10.2 (audit), 10.4 (log integrity) |
| **ISO 27001:2022** | A.8 (asset mgmt), A.9 (access), A.12 (ops security), A.18 (compliance) |
| **GDPR** Art. 5, 32 | Encryption (Art. 32), pseudonymization, access controls, data breach procedures |
| **OWASP ASVS v4.0.3** | V2 (auth), V3 (session), V4 (access), V5 (validation), V6 (storage), V7 (crypto) |
