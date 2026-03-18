#!/bin/bash
set -e

# Start Ollama server in background
ollama serve &
SERVER_PID=$!

# Wait for Ollama to be ready
echo "[AIRGAP] Waiting for Ollama server..."
for i in $(seq 1 60); do
    if curl -sf http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo "[AIRGAP] Ollama is ready."
        break
    fi
    sleep 1
done

# Check and pull model (only works during build or first online run)
MODEL="${LLM_MODEL:-llama3:8b-instruct-q4_K_M}"
if ! ollama list | grep -q "$MODEL"; then
    echo "[AIRGAP] Model $MODEL not found. Attempting pull..."
    ollama pull "$MODEL" || echo "[AIRGAP] WARNING: Pull failed. Ensure model is pre-loaded for offline use."
else
    echo "[AIRGAP] Model $MODEL verified and ready."
fi

# Keep server running
wait $SERVER_PID
