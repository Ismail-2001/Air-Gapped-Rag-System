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
- **security:** AES-256-GCM encryption at rest with PBKDF2 key derivation
- **feat(observability):** Structured JSON logging configuration
- **feat(retrieval):** Hybrid retrieval with BM25 + vector search and RRF fusion
- **feat(retrieval):** Similarity threshold filtering (score_threshold=0.7)
- **feat(retrieval):** Query expansion with multi-query generation and deduplication
- **feat(retrieval):** Cross-encoder reranking for precision improvement
- **feat(citations):** Metadata preservation with source/page tracking in context
- **feat(chunking):** Semantic sentence-aware document chunking
- **feat(infra):** nginx TLS 1.3 reverse proxy with HSTS and security headers
- **feat(infra):** Kubernetes manifests (namespace, config, secrets, PVC, deployments, services, network policy)
- **feat(infra):** Prometheus metrics endpoint with query/reranker/LLM latency tracking
- **feat(ops):** Backup and restore scripts with optional encryption
- **feat(ops):** Self-signed certificate provisioning for development
- **feat(ops):** Compliance documentation with SOC2, NIST, PCI, ISO, GDPR mappings
- **feat(ops):** Chaos engineering shell tests (network partition, process kill, disk pressure, corruption, load spike)

### Fixes
- **fix(airgap):** Pre-load Ollama model during Docker build to enable offline startup
- **fix:** Pin base images to specific hashes — remove `:latest` tags

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
- Added 14 integration tests for full pipeline (PDF, auth, rate-limit, audit, crypto, security)
- Added 5 chaos engineering unit tests (resilience patterns)
- Added chaos engineering shell test suite (network, process, disk, corruption, load)
- Created test infrastructure with `conftest.py` and shared fixtures

## v1.0.0 (Original Release)
- Initial proof-of-concept with LCEL RAG pipeline
- Docker Compose orchestration with GPU passthrough
- Prompt injection shielding
- Air-gapped network isolation
- Streamlit tactical UI in formal military Spanish
