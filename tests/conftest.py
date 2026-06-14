"""
Shared test fixtures for Fortaleza Digital test suite.
"""

import os
import sys
import tempfile
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "app"))


@pytest.fixture
def temp_dir():
    """Provide a temporary directory for test artifacts."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def sample_pdf_bytes():
    """Return minimal valid PDF bytes for testing."""
    return b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n3 0 obj<</Type/Page/MediaBox[0 0 612 792]>>endobj\nxref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \ntrailer<</Size 4/Root 1 0 R>>\nstartxref\n190\n%%EOF"


@pytest.fixture
def mock_config(monkeypatch):
    """Patch config module with test defaults."""
    import config as cfg_mod
    monkeypatch.setattr(cfg_mod.config, "EMBEDDING_DEVICE", "cpu")
    monkeypatch.setattr(cfg_mod.config, "CHUNK_SIZE", 500)
    monkeypatch.setattr(cfg_mod.config, "CHUNK_OVERLAP", 100)
    monkeypatch.setattr(cfg_mod.config, "TOP_K_RESULTS", 4)
    monkeypatch.setattr(cfg_mod.config, "SIMILARITY_THRESHOLD", 0.0)
    monkeypatch.setattr(cfg_mod.config, "MAX_TOKENS", 128)
    monkeypatch.setattr(cfg_mod.config, "TOP_K", 40)
    monkeypatch.setattr(cfg_mod.config, "TOP_P", 0.9)
    monkeypatch.setattr(cfg_mod.config, "LLM_MODEL", "llama3")
    monkeypatch.setattr(cfg_mod.config, "OLLAMA_BASE_URL", "http://localhost:11434")
    monkeypatch.setattr(cfg_mod.config, "EMBEDDING_MODEL", "BAAI/bge-m3")
    monkeypatch.setattr(cfg_mod.config, "CHROMA_PERSIST_DIR", "/tmp/test_chroma")
    monkeypatch.setattr(cfg_mod.config, "DOCUMENTS_DIR", "/tmp/test_docs")
    monkeypatch.setattr(cfg_mod.config, "FORTALEZA_JWT_SECRET", "test-secret")
    monkeypatch.setattr(cfg_mod.config, "FORTALEZA_SESSION_TTL", 480)
    monkeypatch.setattr(cfg_mod.config, "FORTALEZA_AUTH_MODE", "local")
    monkeypatch.setattr(cfg_mod.config, "FORTALEZA_ADMIN_PASSWORD", "admin")
    monkeypatch.setattr(cfg_mod.config, "FORTALEZA_ENCRYPTION_KEY", "")
    monkeypatch.setattr(cfg_mod.config, "FORTALEZA_RATE_LIMIT", 30)
    monkeypatch.setattr(cfg_mod.config, "SEMANTIC_CHUNKING", False)
    monkeypatch.setattr(cfg_mod.config, "CROSS_ENCODER_MODEL", "cross-encoder/ms-marco-TinyBERT-L-2-v2")
    monkeypatch.setattr(cfg_mod.config, "ENABLE_RERANKER", False)
    yield cfg_mod.config
