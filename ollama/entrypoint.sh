#!/bin/bash
set -euo pipefail

echo "[FORTALEZA] Iniciando servidor Ollama..."
ollama serve &
SERVER_PID=$!

echo "[FORTALEZA] Esperando que Ollama esté listo..."
for i in $(seq 1 90); do
    if curl -sf http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo "[FORTALEZA] Ollama operativo."
        break
    fi
    if [ "$i" -eq 90 ]; then
        echo "[FORTALEZA] ERROR: Ollama no respondió en 90 segundos."
        exit 1
    fi
    sleep 1
done

MODEL="${LLM_MODEL:-llama3:8b-instruct-q4_K_M}"

if ! ollama list | grep -q "$MODEL"; then
    echo "[FORTALEZA] FATAL: Modelo $MODEL no encontrado."
    echo "[FORTALEZA] El modelo debe pre-cargarse durante la construccion de la imagen."
    echo "[FORTALEZA] Ejecute: docker compose build --no-cache ollama"
    exit 1
fi

echo "[FORTALEZA] Modelo $MODEL verificado y operativo."

if command -v nvidia-smi &> /dev/null; then
    echo "[FORTALEZA] GPU detectada:"
    nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader
else
    echo "[FORTALEZA] Sin GPU — ejecutando en modo CPU."
fi

wait $SERVER_PID
