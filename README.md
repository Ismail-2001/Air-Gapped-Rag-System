# 🛡️ Air-Gapped RAG System

**Uncompromised Document Intelligence for High-Security Environments.**

The Air-Gapped RAG (Retrieval-Augmented Generation) system is a production-grade, fully offline solution designed for the analysis of sensitive, classified, or proprietary documents. Built on a foundation of local-only compute, it leverages `Llama 3` and `sentence-transformers` to provide intelligent query responses without ever touching the public internet. Zero API calls. Zero telemetry. Zero data leakage.

---

## 🏗️ ARCHITECTURE

```text
┌─────────────────────────────────────────────────────────┐
│                    Docker Compose Stack                   │
│                  Network: internal only                   │
│                                                           │
│  ┌─────────────────┐         ┌────────────────────────┐  │
│  │    Ollama        │         │   App Container         │  │
│  │    Container     │◄────────│                         │  │
│  │                  │  HTTP   │   Streamlit (UI)        │  │
│  │  llama3:8b-      │ :11434  │   LangChain (RAG)      │  │
│  │  instruct-q4_K_M │         │   ChromaDB (in-process) │  │
│  │                  │         │   sentence-transformers  │  │
│  └─────────────────┘         │   (local embeddings)    │  │
│                               │                         │  │
│                               │   Port 8501 exposed     │  │
│                               └────────────────────────┘  │
│                                                           │
│  Volumes:                                                 │
│  - ./documents:/app/documents  (user PDFs)                │
│  - ./models:/root/.ollama      (Ollama model cache)       │
└─────────────────────────────────────────────────────────┘
```

---

## 🔒 SECURITY GUARANTEES

1.  **Zero External API Calls**: All computation is performed locally. There is no code path or configuration that allows communication with external LLM providers (OpenAI, Anthropic, etc.).
2.  **No Internet at Runtime**: The Docker network is explicitly set to `internal: true`, which disables all outbound traffic from the containers.
3.  **Local Persistence**: All vector embeddings and model weights are stored on the local filesystem. No data is sent to a cloud-based vector database.
4.  **No Telemetry**: All analytical and crash-reporting telemetry is disabled by default via environment variables.

---

## 💻 PREREQUISITES

*   **Docker & Docker Compose**: V2.0+ required.
*   **RAM**: Minimum 16GB (8GB dedicated to Ollama).
*   **Disk**: 10GB for model weights and system image.
*   **CPU**: Modern multi-core CPU (AVX2 support recommended).
*   **OS**: Linux, Windows (WSL2), or macOS.

---

## 🚀 QUICK START (ONLINE BUILD)

1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/Ismail-2001/Air-Gapped-Rag-System.git
    cd Air-Gapped-Rag-System
    ```
2.  **Build Images**:
    ```bash
    make build
    ```
    *Note: This step requires internet to download the LLM and embedding models.*
3.  **Start the Stack**:
    ```bash
    make up
    ```
4.  **Access Terminal**:
    Open `http://localhost:8501` in your browser.
5.  **Secure Ingestion**:
    Upload your PDF documents and click **EXECUTE INGESTION**.

---

## ⛓️ OFFLINE DEPLOYMENT GUIDE (AIR-GAP)

To deploy to a computer with **zero internet access**, follow these steps:

1.  **Build Locally**: On an internet-connected machine, run `make build`.
2.  **Export Images**: 
    ```bash
    make save
    ```
3.  **Transfer Data**: Copy the `exports/` folder, the project source, and any documents to a secured USB drive.
4.  **Load to Target**: On the air-gapped machine:
    ```bash
    make load
    ```
5.  **Run Pipeline**:
    ```bash
    make up
    ```

---

## ⚙️ CONFIGURATION (ENVIRONMENT VARIABLES)

| Variable | Default Value | Description |
| :--- | :--- | :--- |
| `LLM_MODEL` | `llama3:8b-instruct-q4_K_M` | Name of the local LLM model to be used. |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | Embedding model for semantic search. |
| `CHUNK_SIZE` | `1000` | Size of document text chunks. |
| `CHUNK_OVERLAP` | `200` | Overlap bits between consecutive chunks. |
| `OLLAMA_BASE_URL` | `http://ollama:11434` | Internal URL for the Ollama service. |

---

## 🔄 MODEL SWAPPING

To use a different model (e.g., `mistral` instead of `llama3`):
1. Update the `LLM_MODEL` in `.env`.
2. Ensure the model is pulled during the online build phase.
3. Run `make build` again.

---

## 🛠️ TROUBLESHOOTING

-   **Ollama Connection Refused**: Ensure the `ollama` container shows as `healthy`. It can take up to 2 minutes for the initial model verification sequence.
-   **Slow Response Times**: RAG operations on CPUs are intensive. Consider increasing Docker's resource allocation or using a smaller LLM model (e.g., `tinyllama`).
-   **RAM Usage**: The `llama3:8b` model consumes approximately 5-6GB of system RAM. Ensure your system meets the requirements.

---

## 📸 SCREENSHOTS

*(Insert Terminal Screenshots Here)*

---

### Author
Ismail Sajid  
[GitHub Profile](https://github.com/Ismail-2001)

### License
MIT License
