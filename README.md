# 🛡️ FORTALEZA DIGITAL (v1.1.0)
### Sovereign Air-Gapped RAG Intelligence System

**Fortaleza Digital** is an SRE-grade, high-security Retrieval-Augmented Generation (RAG) platform purpose-built for military or corporate environments where data cannot leave the room. It leverages local Large Language Models (LLMs) and Vector Databases to provide intelligent document insights without a single byte of internet connectivity.

---

## 🏛️ ARCHITECTURE & SRE-GRADE DESIGN

Unlike standard RAG implementations, Fortaleza Digital is engineered for **Absolute Isolation**:

- **Local LLM Engine**: [Ollama](https://ollama.com/) running **Llama 3 (8B, Q4_K_M Quantized)**. Optimised for consumer-grade NVIDIA hardware (e.g., ASUS ROG laptops with <6GB VRAM).
- **Hardened Embedding Layer**: **BAAI/BGE-M3** (Multilingual Embeddings) baked into the Docker image. Zero external calls guaranteed via `TRANSFORMERS_OFFLINE=1` and `HF_HUB_OFFLINE=1`.
- **Advanced RAG (LCEL)**: Built using the modern **LangChain Expression Language (LCEL)** for granular control over the retrieval pipeline, bypassing legacy wrappers.
- **Poisoned PDF Defense (Prompt Shielding)**: Custom sanitization layer that neutralizes "Prompt Injection" attacks within documents (e.g., "ignore previous instructions") using regex-based filtering and explicit context delimitation.

## ⚡ CORE CAPABILITIES

- **100% Offline operation**: Containerized network isolation (`internal: true`).
- **Tactical UX**: Pure-black terminal-style interface (#00FF00) localized in **Formal Military Spanish**.
- **Wheel-house Dependencies**: Transitive sub-dependencies are pre-cached during build (`pip download --no-index`) to prevent "dependency hell" during offline deployments.
- **GPU Passthrough**: Native NVIDIA/CUDA support for WSL2 and Linux with automatic CPU-fallback.

---

## 🚀 QUICK START (Windows WSL2 / Linux)

Ensure [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html) is installed on the host.

### 1. Launch System
```bash
docker compose up -d
```
Access the Tactical Terminal at: `http://localhost:8501`

### 2. Manual Ingestion
Simply **Drag-and-Drop** your PDFs into the terminal-styled sidebar. The system will automatically:
1. Extract text using table-aware `pdfplumber`.
2. Sanitize content for prompt injections.
3. Index chunks into a local ChromaDB instance.

---

## 📂 PROJECT STRUCTURE

```bash
├── app/                  # Streamlit UI + LCEL RAG Engine
│   ├── prompt_shield.py   # Security & Sanitization Layer
│   ├── rag_engine.py      # Core Intelligence Logic (LCEL)
│   └── locales.py         # Formal Spanish Localization
├── ollama/               # Offline LLM Server Logic
├── documents/            # Local document store (gitignored)
├── models/               # Persistence for model weights
└── tests/                # Security & License Audit Suite
```

## 🔐 SECURITY & COMPLIANCE

- **Zero-Persistence Option**: Entire vector store can be purged via a single command (available in the UI).
- **License Compliance**: 100% Commercial-friendly (MIT / Apache 2.0). No GPL/AGPL dependencies.
- **Air-Gapped Build Tooling**: Use `prep_offline.ps1` to bundle Docker images for USB transfer.

---

## ⚖️ LICENSE

Distributed under the **MIT License**. Created by **Fortaleza Digital 2026** for Sovereign Intelligence Management.

---
**DOCUMENT CLASSIFICATION**: UNCLASSIFIED // PROOF-OF-CONCEPT
**LEAD ARCHITECT**: [Ismail-2001](https://github.com/Ismail-2001)
