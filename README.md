# FORTALEZA DIGITAL

Sistema RAG (Retrieval-Augmented Generation) soberano, aislado y de grado militar para la gestión de inteligencia documental en entornos sin conexión.

## 🛡️ Características Principales

- **100% Offline**: Cero llamadas externas. Aislado por red de Docker (`internal: true`).
- **Soberanía de Datos**: Procesamiento local en hardware NVIDIA (WSL2) o CPU.
- **Interfaz Táctica**: Terminal de baja firma visual, 100% en español formal.
- **Escudo Anti-Inyección**: Sanitización de PDF para prevenir ataques de prompt injection.
- **Licencia Segura**: 100% libre de dependencias GPL.

## 🚀 Inicio Rápido

Consulte [DEPLOYMENT.md](DEPLOYMENT.md) para instrucciones detalladas de instalación en WSL2 + NVIDIA.

```bash
docker compose up -d
```

Acceda a la terminal: `http://localhost:8501`

## 🛠️ Estructura del Proyecto

- `app/`: Aplicación Streamlit y motor RAG.
- `ollama/`: Servidor de modelos locales.
- `models/`: Pesos del modelo GGUF persistidos.
- `documents/`: Almacén de PDF untrusted.
- `tests/`: Auditoría de seguridad y red.

## ⚖️ Licencia

MIT - Fortaleza Digital 2026.
