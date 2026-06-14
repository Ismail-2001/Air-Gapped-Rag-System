# Fortaleza Digital — Staging Validation Plan

## 1. Hardware Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| CPU | 8 cores (x86_64) | 16 cores |
| RAM | 32 GB | 64 GB |
| GPU | NVIDIA GTX 3060 (6 GB VRAM) | NVIDIA RTX 4090 (24 GB) |
| Storage | 100 GB NVMe | 500 GB NVMe |
| Network | None (air-gapped) | None (air-gapped) |
| OS | Ubuntu 22.04 LTS / Windows WSL2 | Ubuntu 24.04 LTS |

## 2. Software Prerequisites

```bash
# Ubuntu 22.04+
sudo apt-get update && sudo apt-get install -y \
    docker-ce docker-ce-cli containerd.io \
    docker-compose-plugin \
    nvidia-driver-545 nvidia-container-toolkit \
    curl jq

# Verify NVIDIA
nvidia-smi

# Verify Docker + GPU passthrough
sudo docker run --rm --gpus all nvidia/cuda:12.4.0-base-ubuntu22.04 nvidia-smi

# Verify Docker Compose
docker compose version
```

## 3. Deployment (Docker Compose)

### 3.1 Clone & Secrets
```bash
git clone https://github.com/Ismail-2001/Air-Gapped-Rag-System.git
cd Air-Gapped-Rag-System

# Generate JWT and encryption keys
bash scripts/generate_secrets.sh

# User prompt: set FORTALEZA_ADMIN_PASSWORD and FORTALEZA_JWT_SECRET
# in .env (copy from .env.example if available)
```

### 3.2 Build Images

**Measured metric: build time should be recorded.**
```bash
# Record start
BUILD_START=$(date +%s)

docker compose build --no-cache

BUILD_END=$(date +%s)
echo "Build duration: $((BUILD_END - BUILD_START)) seconds"
```

### 3.3 Launch

```bash
docker compose up -d

# Wait for health checks
sleep 30

# Verify all services healthy
docker compose ps
docker compose logs --tail=20 nginx
docker compose logs --tail=20 app
docker compose logs --tail=20 ollama
```

### 3.4 Network Isolation Verification

```bash
# Confirm no egress possible from any container
docker exec fortaleza-app curl -sf --connect-timeout 5 https://google.com && \
    echo "FAIL: egress detected" || echo "PASS: no egress"
docker exec fortaleza-ollama ping -c 1 8.8.8.8 && \
    echo "FAIL: egress detected" || echo "PASS: no egress"
```

### 3.5 TLS Termination Verification

```bash
# Should redirect HTTP -> HTTPS and serve TLS 1.3
curl -skI https://localhost | grep -i "strict-transport-security" && \
    echo "PASS: HSTS header present" || echo "FAIL: no HSTS"
curl -sk https://localhost/health && echo "" || echo "FAIL: health endpoint"

# Verify TLS 1.3 only (should fail with --tls-max 1.2)
curl -sk --tls-max 1.2 https://localhost/health 2>&1 || \
    echo "PASS: TLS 1.2 rejected"
```

## 4. Functional Validation

### 4.1 Authentication

```bash
# Login as admin (default password: admin unless changed in .env)
TOKEN=$(curl -sk -X POST https://localhost/auth/login \
    -H "Content-Type: application/json" \
    -d '{"username":"admin","password":"admin"}' | jq -r '.token')

echo "Token: ${TOKEN:0:20}..."

# Verify token
curl -sk -X POST https://localhost/auth/verify \
    -H "Authorization: Bearer $TOKEN" | jq .

# Invalid login must fail
curl -sk -X POST https://localhost/auth/login \
    -H "Content-Type: application/json" \
    -d '{"username":"admin","password":"wrong"}' | jq .error
```

### 4.2 Document Ingestion

```bash
# Needs a test PDF: generate one
cat > /tmp/test_doc.txt << 'EOF'
PROCEDIMIENTO OPERATIVO ESTÁNDAR: MANTENIMIENTO DE GENERADORES

1. El oficial de guardia debe verificar el nivel de combustible cada 4 horas.
2. El generador debe someterse a mantenimiento preventivo cada 500 horas de operación.
3. Cualquier anomalía en las lecturas de voltaje debe reportarse inmediatamente al supervisor.
4. El personal autorizado debe portar equipo de protección personal en todo momento.
5. Los registros de mantenimiento deben archivarse por un período mínimo de 5 años.
EOF

# Convert to PDF using Python
python3 -c "
from fpdf import FPDF
pdf = FPDF()
pdf.add_page()
pdf.set_font('Courier', size=10)
with open('/tmp/test_doc.txt') as f:
    for line in f:
        pdf.cell(0, 5, txt=line.strip(), new_x='LMARGIN', new_y='NEXT')
pdf.output('/tmp/test_doc.pdf')
print('Created /tmp/test_doc.pdf')
"

# Ingestion (assumes Streamlit UI at https://localhost)
# For API-based ingestion:
curl -sk -X POST https://localhost/ingest \
    -H "Authorization: Bearer $TOKEN" \
    -F "file=@/tmp/test_doc.pdf" | jq .
```

### 4.3 Query

```bash
curl -sk -X POST https://localhost/query \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"question":"Cada cuantas horas debe verificarse el nivel de combustible?"}' | jq .
```

## 5. Chaos Engineering Execution

### 5.1 Run Chaos Test Suite

**This is the critical gate for v2.0.0. All tests must pass.**
```bash
# Clone has the test suite at tests/chaos_test.sh
bash tests/chaos_test.sh all
```

| Test | What it does | Success criteria | Expected duration |
|------|-------------|-----------------|-------------------|
| `network` | Disconnect `fortaleza-app` from `airgap-net` | App cannot reach ollama; recovers after reconnect | 30 s |
| `process` | Kill streamlit process inside app container | Container restarts via `restart: unless-stopped` | 20 s |
| `disk` | Write 50 MB junk to audit_log volume | App handles disk pressure without crash | 10 s |
| `ollama` | Restart ollama container mid-session | App reconnects after ollama restart | 20 s |
| `corrupt` | Write random bytes to ChromaDB directory | App initializes despite corrupted data | 10 s |
| `load` | Fire 50 concurrent rate-limit checks | Rate limiter blocks after window exceeded | 15 s |

### 5.2 Manual Chaos Extensions (if staging is available for destructive testing)

```bash
# Memory pressure
docker update --memory 512m fortaleza-app
# Wait 30s, then verify app still responds to health check

# CPU pressure
docker exec fortaleza-app stress --cpu 4 --timeout 30

# DNS failure (air-gap enforced)
docker exec fortaleza-app sh -c "echo 'nameserver 1.1.1.1' > /etc/resolv.conf"
# verify network policy overrides this
```

## 6. Benchmarking

### 6.1 Query Latency

```bash
# Run 20 queries, measure p50/p95/p99 latency
for i in $(seq 1 20); do
    START=$(date +%s%N)
    curl -sk -X POST https://localhost/query \
        -H "Authorization: Bearer $TOKEN" \
        -H "Content-Type: application/json" \
        -d "{\"question\":\"Cual es el procedimiento para mantenimiento de generadores?\"}" \
        -o /dev/null -w '%{http_code}' 2>/dev/null
    END=$(date +%s%N)
    echo "$(( (END - START) / 1000000 )) ms"
done | awk '{print $1}' > /tmp/latencies.txt

# Calculate percentiles
sort -n /tmp/latencies.txt | awk '
{vals[NR]=$1}
END{
    n=NR
    print "p50: " vals[int(n*0.5)]
    print "p95: " vals[int(n*0.95)]
    print "p99: " vals[int(n*0.99)]
    print "min: " vals[1]
    print "max: " vals[n]
}'
```

**Acceptance criteria:**
- p50 latency < 5 seconds
- p95 latency < 15 seconds  
- p99 latency < 30 seconds
- Zero errors (all HTTP 200)

### 6.2 Prometheus Metrics

```bash
# Scrape the metrics endpoint
curl -sk http://localhost:8000/metrics | grep fortaleza

# Expected output samples:
#   fortaleza_queries_total{status="success",user_role="admin"} 20
#   fortaleza_query_latency_seconds_bucket{le="5.0"} 15
#   fortaleza_llm_latency_seconds_bucket{le="10.0"} 20
#   fortaleza_active_sessions 1
```

### 6.3 Memory & GPU Utilization

```bash
# Monitor during benchmark
nvidia-smi --query-gpu=memory.used,utilization.gpu --format=csv -l 2

# Container resource usage
docker stats --no-stream --format '{{.Name}}\t{{.MemPerc}}\t{{.CPUPerc}}'
```

**Acceptance criteria:**
- GPU memory < 6 GB (consumer hardware compatibility)
- Container memory < 4 GB per service
- CPU < 80% sustained

## 7. Rollback Plan

| Scenario | Action | RTO |
|----------|--------|-----|
| Build failure | Revert to last known-good image tag | 5 min |
| Service crash loop | `docker compose down && docker compose up -d` | 2 min |
| Corrupted vector store | `docker compose down && rm -rf chroma_data && bash scripts/restore.sh <backup>` | 15 min |
| Security breach | Rotate all secrets, rebuild with `--no-cache`, restore from pre-breach backup | 30 min |
| Hardware failure | Migrate volumes to standby node, redeploy | 1 hour |

## 8. go/no-go Gates for v2.0.0

All gates must pass before tagging v2.0.0:

| # | Gate | Check | Pass/Fail |
|---|------|-------|-----------|
| 1 | Build completes | `docker compose build` exits 0 | |
| 2 | All containers healthy | `docker compose ps` shows all 3 `Up` | |
| 3 | Network isolation | No egress from any container | |
| 4 | TLS 1.3 only | TLS 1.2 rejected, HSTS present | |
| 5 | JWT auth works | Login, verify, invalid login all behave correctly | |
| 6 | Document ingestion | PDF can be ingested without error | |
| 7 | Query returns results | RAG produces coherent response with citations | |
| 8 | Chaos suite passes | `tests/chaos_test.sh all` → 0 failures | |
| 9 | Latency within SLA | p50 < 5s, p95 < 15s, p99 < 30s | |
| 10 | GPU memory within limit | < 6 GB VRAM | |
| 11 | Metrics endpoint responds | `curl localhost:8000/metrics` returns data | |
| 12 | Audit chain intact | `GET /audit/verify` returns `{"valid": true}` | |

## 9. v2.0.0 Release Checklist

```bash
# 1. Tag the release
git tag -a v2.0.0 -m "Fortaleza Digital v2.0.0 — production-ready air-gapped RAG"
git push origin v2.0.0

# 2. Build production images (pinned digests)
docker compose build

# 3. Export images for air-gapped transfer
docker save fortaleza-app:latest fortaleza-ollama:latest fortaleza-nginx:latest \
    | gzip > fortaleza-v2.0.0-images.tar.gz

# 4. Bundle offline dependencies
bash scripts/prep_offline.sh  # if available

# 5. Sign images (if Cosign configured)
cosign sign --key cosign.key fortaleza-app:latest
```
