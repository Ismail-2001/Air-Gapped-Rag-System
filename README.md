# FORTALEZA DIGITAL
### Sovereign Air-Gapped RAG Intelligence System

**Fortaleza Digital** is an SRE-grade, high-security Retrieval-Augmented Generation (RAG) platform purpose-built for air-gapped environments. It leverages local LLMs and Vector Databases to provide intelligent document insights without any internet connectivity.

---

## ARCHITECTURE & SRE-GRADE DESIGN

- **Local LLM Engine**: Ollama running **Llama 3 (8B, Q4_K_M Quantized)**. Pre-loaded during Docker build for zero runtime downloads.
- **Hardened Embedding Layer**: **BAAI/BGE-M3** (Multilingual) baked into the image. Zero external calls via `TRANSFORMERS_OFFLINE=1`.
- **Hybrid Retrieval**: BM25 keyword search + vector similarity with Reciprocal Rank Fusion (RRF).
- **Query Expansion**: Multi-query generation via LLM for improved recall and deduplication.
- **Semantic Chunking**: Sentence-aware document splitting that respects paragraph boundaries.
- **Prompt Injection Defense**: 40+ regex patterns blocking DAN, jailbreak, Unicode, and multilingual attacks.
- **Immutable Audit Chain**: HMAC-SHA256 integrity-verified event log with tamper detection.
- **JWT Authentication**: RBAC with 7 roles, clearance levels, and PBKDF2 password hashing.
- **Encryption at Rest**: AES-256-GCM with PBKDF2-derived keys for document and backup encryption.
- **TLS 1.3 Termination**: nginx reverse proxy with HSTS, security headers, and self-signed cert provisioning.
- **Air-Gapped Validation**: Pre-commit hooks, ruff/mypy/bandit linting, and CI/CD quality gates.

## CORE CAPABILITIES

- **100% Offline**: Containerized network isolation (`internal: true`), pre-cached models and dependencies.
- **Tactical UX**: Terminal-style interface localized in **Formal Military Spanish**.
- **GPU Passthrough**: Native NVIDIA/CUDA for WSL2/Linux with automatic CPU-fallback.
- **Structured Logging**: JSON-formatted observability output.
- **Rate Limiting**: Per-user sliding window (configurable, default 30 req/min).
- **Input Validation**: Injection pattern blocking for all user queries.

---

## PROJECT STRUCTURE

```bash
├── app/                     # Streamlit UI + RAG Engine
│   ├── auth.py              # JWT authentication (RBAC, clearance levels)
│   ├── audit.py             # Immutable audit chain (HMAC-SHA256)
│   ├── chunking.py          # Semantic chunking (sentence-aware)
│   ├── config.py            # Centralized environment config
│   ├── crypto.py            # AES-256-GCM encryption at rest
│   ├── input_validator.py   # Query injection blocking
│   ├── locales.py           # Formal Spanish localization
│   ├── logging_config.py    # Structured JSON logging
│   ├── pdf_processor.py     # PDF extraction + chunking pipeline
│   ├── prompt_shield.py     # 40+ injection pattern defense
│   ├── query_expansion.py   # Multi-query expansion + dedup
│   ├── rag_engine.py        # Core RAG orchestration
│   ├── rate_limiter.py      # Per-user sliding window rate limiter
│   ├── retrieval.py         # Hybrid BM25 + vector retrieval (RRF)
│   └── streamlit_app.py     # Streamlit tactical UI
├── nginx/                   # TLS 1.3 reverse proxy
│   ├── Dockerfile           # Pinned Alpine-based nginx
│   ├── nginx.conf           # TLS 1.3 only, HSTS, security headers
│   └── provision-ssl.sh     # Self-signed cert generator (dev)
├── ollama/                  # Offline LLM server
│   ├── Dockerfile           # Pre-loads model during build
│   └── entrypoint.sh        # Fails fast if model missing
├── k8s/                     # Kubernetes manifests (9 resources)
│   ├── 00-namespace.yaml    # fortaleza namespace
│   ├── 01-configmap.yaml    # Environment configuration
│   ├── 02-secrets.yaml      # JWT/encryption secrets
│   ├── 03-pvc.yaml          # Persistent volume claims
│   ├── 10-ollama.yaml       # Ollama deployment + service
│   ├── 20-app.yaml          # App deployment (2 replicas) + service
│   ├── 30-nginx.yaml        # Nginx deployment + service
│   ├── 31-nginx-configmap.yaml
│   └── 40-network-policy.yaml
├── scripts/
│   ├── backup.sh            # Timestamped volume backup with encryption
│   ├── restore.sh           # Backup restoration (supports .enc)
│   └── generate_secrets.sh  # JWT/encryption key generation
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Shared fixtures
│   ├── test_auth.py         # 17 auth unit tests
│   └── test_audit.py        # 10 audit unit tests
├── .github/workflows/
│   ├── ci.yml               # Lint + test + security checks
│   └── security-scan.yml    # Trivy, Gitleaks, pip-audit, license scan
├── docker-compose.yml       # Orchestration (ollama, app, nginx)
├── Makefile                 # Test/lint/clean/quality gate targets
├── pyproject.toml           # Ruff, mypy, bandit, pytest config
└── .pre-commit-config.yaml  # Automated code quality
```

## QUICK START (Windows WSL2 / Linux)

Ensure [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html) is installed on the host.

### 1. Generate Secrets
```bash
bash scripts/generate_secrets.sh
```

### 2. Launch System
```bash
make build
make up
```

Access the Tactical Terminal at: `https://localhost` (TLS 1.3)

### 3. Common Operations
```bash
make test-all       # Run all tests
make lint           # Run all linters (ruff, mypy, bandit)
make quality-gate   # CI entry point: lint + test
make backup         # Run backup script
```

## AUTHENTICATION

The system enforces JWT-based authentication with 7 RBAC roles:

| Role         | Clearance | Permissions |
|-------------|-----------|-------------|
| viewer      | 1         | Read queries only |
| analyst     | 2         | Query + view audit log |
| ingestor    | 3         | + Document ingestion |
| operator    | 4         | + Database purge |
| auditor     | 5         | + Full audit log access |
| admin       | 6         | + User management |
| superadmin  | 7         | All operations |

## API ENDPOINTS

| Endpoint       | Method | Auth | Description |
|---------------|--------|------|-------------|
| `/health`     | GET    | No   | Health check |
| `/auth/login` | POST   | No   | Obtain JWT token |
| `/auth/verify`| POST   | Yes  | Verify token validity |
| `/query`      | POST   | Yes  | Submit RAG query |
| `/ingest`     | POST   | Yes  | Ingest documents |
| `/audit/log`  | GET    | Yes  | Retrieve audit log |
| `/audit/verify`| GET   | Yes  | Verify audit chain integrity |

## SECURITY COMPLIANCE

- **Zero-Persistence**: Database purge available via UI or API.
- **License Compliance**: 100% MIT/Apache 2.0 — no GPL/AGPL dependencies.
- **Image Scanning**: Automated Trivy scans for critical/high CVEs in CI.
- **Secret Detection**: Gitleaks runs on every push to prevent credential leaks.
- **Dependency Auditing**: pip-audit and safety checks in CI.
- **Air-Gapped Build**: All models and dependencies pre-cached during Docker build.

---

## LICENSE

Distributed under the **MIT License**. Created by **Fortaleza Digital 2026** for Sovereign Intelligence Management.

---
**DOCUMENT CLASSIFICATION**: UNCLASSIFIED // PROOF-OF-CONCEPT
**LEAD ARCHITECT**: [Ismail-2001](https://github.com/Ismail-2001)
