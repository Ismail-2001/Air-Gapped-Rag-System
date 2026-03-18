# GUÍA DE DESPLIEGUE SECTORIAL — FORTALEZA DIGITAL

Este documento detalla los pasos exactos para implementar el sistema en un entorno aislado (Air-Gapped) utilizando **WSL2** y hardware **NVIDIA** (ASUS ROG o similar).

---

## 🔧 REQUISITOS PREVIOS (Entorno Host Windows)

1.  **Drivers NVIDIA**: Instale la versión más reciente desde [nvidia.com/drivers](https://www.nvidia.com/drivers).
2.  **WSL2**: Ejecute `wsl --install` y configure Ubuntu 22.04 LTS.
3.  **Docker Desktop**: Instale y active el backend de WSL2 en la configuración.

---

## 🛠️ PASO 1: INSTALACIÓN DEL TOOLKIT NVIDIA (Dentro de WSL2)

Ejecute los siguientes comandos dentro de su terminal de Ubuntu:

```bash
# Configurar el repositorio para NVIDIA Container Toolkit
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg \
  && curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
    sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
    sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

# Instalar el toolkit
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit

# Configurar el runtime de Docker
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```

**Verificación**: `docker run --rm --gpus all nvidia/cuda:12.0-base nvidia-smi` (Debe mostrar la GPU).

---

## 📂 PASO 2: TRANSFERENCIA AL ENTORNO AISLADO

Si el entorno no tiene internet, descargue las imágenes en una máquina conectada:

```bash
# En máquina con internet:
docker compose build
docker save fortaleza-ollama:latest | gzip > fortaleza-ollama.tar.gz
docker save fortaleza-app:latest | gzip > fortaleza-app.tar.gz

# --- Transferir via USB a la máquina aislada ---

# En máquina aislada:
docker load < fortaleza-ollama.tar.gz
docker load < fortaleza-app.tar.gz
```

---

## ⚡ PASO 3: LANZAMIENTO DEL SISTEMA

### PERFIL GPU (Por defecto - Recomendado)
```bash
docker compose up -d
```

### PERFIL CPU (Fallback si no hay hardware NVIDIA)
```bash
docker compose -f docker-compose.yml -f docker-compose.cpu.yml up -d
```

### MONITOREO DE INICIO
```bash
docker compose logs -f ollama
```

---

## 🏁 PASO 4: ACCESO OPERATIVO

Una vez que los registros indiquen `[FORTALEZA] OPERATIVO`, acceda a:

**Terminal Táctico**: `http://localhost:8501`

---

## 🔐 PROTOCOLO DE PURGA

Para eliminar todo rastro de documentos y base de datos vectorial:

```bash
# Método 1: Via Interfaz (Botón PURGAR en barra lateral)
# Método 2: Via Terminal
rm -rf chroma_data/*
rm -rf documents/*.pdf
```

---
**ESTADO DEL DOCUMENTO**: CLASIFICADO - SÓLO USO INTERNO
**VERSIÓN**: 1.0.0
