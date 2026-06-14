FROM ollama/ollama:0.3.14@sha256:13d63e7eea0a0c25c96d1d88df5c152e5a519e2e1d1e9c0b8e7ff96f04fb5c1a

ARG LLM_MODEL=llama3:8b-instruct-q4_K_M

RUN ollama serve & \
    SERVER_PID=$! && \
    for i in $(seq 1 30); do \
        if curl -sf http://localhost:11434/api/tags > /dev/null 2>&1; then \
            break; \
        fi; \
        sleep 1; \
    done && \
    ollama pull ${LLM_MODEL} && \
    kill $SERVER_PID && \
    wait $SERVER_PID 2>/dev/null

RUN ollama list | grep -q "${LLM_MODEL}" || exit 1

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

RUN groupadd -r fortaleza -g 1000 && \
    useradd -r -g fortaleza -u 1000 -m -d /home/fortaleza fortaleza

USER fortaleza

ENTRYPOINT ["/entrypoint.sh"]
