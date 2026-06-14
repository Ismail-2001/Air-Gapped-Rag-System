"""Configuración central del sistema Fortaleza Digital."""

import os
from dataclasses import dataclass


@dataclass
class Config:
    """Configuración cargada desde variables de entorno."""
    
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "llama3:8b-instruct-q4_K_M")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "BAAI/bge-m3")
    EMBEDDING_DEVICE: str = os.getenv("EMBEDDING_DEVICE", "cpu")
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "1000"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "200"))
    TOP_K_RESULTS: int = int(os.getenv("TOP_K_RESULTS", "4"))
    SIMILARITY_THRESHOLD: float = float(os.getenv("SIMILARITY_THRESHOLD", "0.7"))
    MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "2048"))
    TOP_K: int = int(os.getenv("TOP_K", "40"))
    TOP_P: float = float(os.getenv("TOP_P", "0.9"))
    DOCUMENTS_DIR: str = os.getenv("DOCUMENTS_DIR", "/app/documents")
    CHROMA_PERSIST_DIR: str = os.getenv("CHROMA_PERSIST_DIR", "/app/chroma_data")
    REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "120"))
    FORTALEZA_JWT_SECRET: str = os.getenv("FORTALEZA_JWT_SECRET", "")
    FORTALEZA_SESSION_TTL: int = int(os.getenv("FORTALEZA_SESSION_TTL", "480"))
    FORTALEZA_AUTH_MODE: str = os.getenv("FORTALEZA_AUTH_MODE", "local")
    FORTALEZA_ADMIN_PASSWORD: str = os.getenv("FORTALEZA_ADMIN_PASSWORD", "admin")
    FORTALEZA_ENCRYPTION_KEY: str = os.getenv("FORTALEZA_ENCRYPTION_KEY", "")
    FORTALEZA_RATE_LIMIT: int = int(os.getenv("FORTALEZA_RATE_LIMIT", "30"))
    SEMANTIC_CHUNKING: bool = os.getenv("SEMANTIC_CHUNKING", "true").lower() == "true"


config = Config()
