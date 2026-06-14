FROM python:3.11-slim@sha256:e3b17e38e6d4d3f0a6e087b5d0d1f2f3c7c8b9a0d1e2f3a4b5c6d7e8f9a0b1c AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build

COPY requirements.txt .
RUN pip install --no-cache-dir pip-tools && \
    pip download -r requirements.txt -d /wheels && \
    echo "[FORTALEZA] Todas las dependencias descargadas como wheels."

FROM python:3.11-slim@sha256:e3b17e38e6d4d3f0a6e087b5d0d1f2f3c7c8b9a0d1e2f3a4b5c6d7e8f9a0b1c

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd -r fortaleza -g 1000 && \
    useradd -r -g fortaleza -u 1000 -m -d /app fortaleza

WORKDIR /app

COPY --from=builder /wheels /wheels

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    TRANSFORMERS_OFFLINE=1 \
    HF_HUB_OFFLINE=1 \
    HF_DATASETS_OFFLINE=1 \
    SENTENCE_TRANSFORMERS_HOME=/app/models

COPY requirements.txt .
RUN pip install --no-cache-dir --no-index --find-links=/wheels -r requirements.txt && \
    rm -rf /root/.cache && \
    echo "[FORTALEZA] Instalacion offline completada."

ENV SENTENCE_TRANSFORMERS_HOME=/app/models
RUN mkdir -p /app/models && \
    python -c "\
from sentence_transformers import SentenceTransformer; \
model = SentenceTransformer('BAAI/bge-m3', cache_folder='/app/models'); \
dim = model.get_sentence_embedding_dimension(); \
print(f'[FORTALEZA] Modelo BGE-M3 cargado: {dim}d embeddings')"

RUN python -c "\
import streamlit; \
import langchain; \
import langchain_community; \
import langchain_huggingface; \
import langchain_ollama; \
import langchain_chroma; \
import chromadb; \
import sentence_transformers; \
import pdfplumber; \
import pydantic; \
import cryptography; \
print('[FORTALEZA] Verificacion de importaciones: TODAS CORRECTAS')"

COPY . .
RUN rm -rf /wheels

RUN chown -R fortaleza:fortaleza /app

USER fortaleza

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -sf http://localhost:8501/_stcore/health || exit 1

CMD ["streamlit", "run", "streamlit_app.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true", \
     "--browser.gatherUsageStats=false"]
