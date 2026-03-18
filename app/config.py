import os
from dataclasses import dataclass

@dataclass
class Config:
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "llama3:8b-instruct-q4_K_M")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", 1000))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", 200))
    TOP_K_RESULTS: int = int(os.getenv("TOP_K_RESULTS", 4))
    DOCUMENTS_DIR: str = os.getenv("DOCUMENTS_DIR", "/app/documents")
    CHROMA_PERSIST_DIR: str = os.getenv("CHROMA_PERSIST_DIR", "/app/chroma_data")
    REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", 120))

config = Config()
