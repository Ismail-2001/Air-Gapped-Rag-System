FROM python:3.11-slim AS builder

# System dependencies for building wheels
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build

# Copy requirements and download ALL wheels (including transitive deps)
COPY requirements.txt .
RUN pip install --no-cache-dir pip-tools && \
    pip download -r requirements.txt -d /wheels && \
    echo "[FORTALEZA] Todas las dependencias descargadas como wheels."

# ── Final Stage ──
FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy pre-downloaded wheels from builder
COPY --from=builder /wheels /wheels

# Install from local wheels ONLY — pip CANNOT reach PyPI
COPY requirements.txt .
RUN pip install --no-cache-dir --no-index --find-links=/wheels -r requirements.txt && \
    echo "[FORTALEZA] Instalación offline completada."

# Pre-download BGE-M3 embedding model into image
# This caches the model inside the Docker layer for offline use
RUN python -c "\
from sentence_transformers import SentenceTransformer; \
model = SentenceTransformer('BAAI/bge-m3'); \
dim = model.get_sentence_embedding_dimension(); \
print(f'[FORTALEZA] Modelo BGE-M3 cargado: {dim}d embeddings')"

# Verify ALL critical imports succeed — fail build if anything is missing
RUN python -c "\
import streamlit; \
import langchain; \
import langchain_community; \
import langchain_huggingface; \
import chromadb; \
import sentence_transformers; \
import pdfplumber; \
print('[FORTALEZA] Verificación de importaciones: TODAS CORRECTAS')"

# Copy application code
COPY . .

# Remove any leftover wheels from final image (save space)
RUN rm -rf /wheels

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -sf http://localhost:8501/_stcore/health || exit 1

CMD ["streamlit", "run", "streamlit_app.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true", \
     "--browser.gatherUsageStats=false"]
