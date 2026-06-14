# CHANGELOG — Fortaleza Digital

## v2.0.0 (Unreleased)

### Breaking Changes
- Authentication required to access the system
- Environment variables added: `FORTALEZA_JWT_SECRET`, `FORTALEZA_SESSION_TTL`, `FORTALEZA_USERS`, `FORTALEZA_ADMIN_PASSWORD`
- Docker volumes added: `audit_logs`

### Features
- **security:** JWT-based authentication with RBAC and clearance levels (#3)
- **security:** Immutable audit logging with chain integrity verification (#4)
- **security:** Enable CORS and XSRF protection (#2)

### Fixes
- **fix(airgap):** Pre-load Ollama model during Docker build to enable offline startup (#1)
- **fix:** Pin base images to specific hashes — remove `:latest` tags

### Security
- Containers now run as non-root user
- Secrets configuration via `.streamlit/secrets.toml`

### Infrastructure
- Added `.dockerignore` to reduce build context
- Added `scripts/generate_secrets.sh` for secret provisioning

## v1.0.0 (Original Release)
- Initial proof-of-concept with LCEL RAG pipeline
- Docker Compose orchestration with GPU passthrough
- Prompt injection shielding
- Air-gapped network isolation
- Streamlit tactical UI in formal military Spanish
