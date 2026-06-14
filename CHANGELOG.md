# CHANGELOG — Fortaleza Digital

## v2.0.0 (Unreleased)

### Breaking Changes
- Authentication required to access the system
- Environment variables added: `FORTALEZA_JWT_SECRET`, `FORTALEZA_SESSION_TTL`, `FORTALEZA_USERS`, `FORTALEZA_ADMIN_PASSWORD`
- Docker volumes added: `audit_logs`

### Features
- **security:** JWT-based authentication with RBAC and clearance levels
- **security:** Immutable audit logging with chain integrity verification
- **security:** Enable CORS and XSRF protection
- **security:** Input validation module for query injection blocking
- **security:** Rate limiting middleware for user queries
- **security:** Enhanced prompt injection shield with 40+ patterns
- **feat(observability):** Structured JSON logging configuration
- **feat(retrieval):** Similarity threshold filtering (score_threshold=0.7)
- **feat(citations):** Metadata preservation with source/page tracking in context

### Fixes
- **fix(airgap):** Pre-load Ollama model during Docker build to enable offline startup
- **fix:** Pin base images to specific hashes — remove `:latest` tags

### Refactors
- **refactor:** Migrate from deprecated `langchain_community` to `langchain_chroma` and `langchain_ollama`
- **refactor:** Replace deprecated `get_relevant_documents()` with `invoke()`
- **refactor:** Remove deprecated `persist()` call (auto-persist in ChromaDB 0.5.x)
- **refactor:** Move LCEL imports to module-level for cleaner code

### Infrastructure
- Added `.dockerignore` to reduce build context
- Added `scripts/generate_secrets.sh` for secret provisioning
- Added `pyproject.toml` with ruff, mypy, bandit, pytest configuration
- Added `.pre-commit-config.yaml` for automated code quality checks
- Added `.github/workflows/ci.yml` with lint, test, and security jobs

### Testing
- Added 17 unit tests for auth module (JWT, RBAC, clearance levels)
- Added 10 unit tests for audit module (chain integrity, tamper detection)
- Created test infrastructure with `conftest.py` and shared fixtures

## v1.0.0 (Original Release)
- Initial proof-of-concept with LCEL RAG pipeline
- Docker Compose orchestration with GPU passthrough
- Prompt injection shielding
- Air-gapped network isolation
- Streamlit tactical UI in formal military Spanish
