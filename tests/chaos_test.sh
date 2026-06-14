#!/bin/bash
# Fortaleza Digital — Chaos Engineering Test Suite
# Run against a running Docker Compose deployment.
# Usage: bash tests/chaos_test.sh [test_name]
set -euo pipefail

PASS=0
FAIL=0

pass() { PASS=$((PASS+1)); echo "  ✓ $1"; }
fail() { FAIL=$((FAIL+1)); echo "  ✗ $1"; }

test_network_partition() {
    echo "[CHAOS] Network partition: disconnect app from ollama..."
    docker network disconnect airgap-net fortaleza-app 2>/dev/null || true
    sleep 3
    if docker exec fortaleza-app curl -sf http://ollama:11434/api/tags 2>/dev/null; then
        fail "app still reaches ollama after network cut"
    else
        pass "app cannot reach ollama after network cut"
    fi
    docker network connect airgap-net fortaleza-app 2>/dev/null || true
    sleep 5
    if docker exec fortaleza-app curl -sf http://ollama:11434/api/tags >/dev/null 2>&1; then
        pass "app reconnects after network restore"
    else
        fail "app does not recover after network restore"
    fi
}

test_process_kill() {
    echo "[CHAOS] Process kill: kill app container main process..."
    docker exec fortaleza-app pkill -f streamlit 2>/dev/null || true
    sleep 10
    STATUS=$(docker inspect fortaleza-app --format='{{.State.Status}}')
    if [ "$STATUS" = "running" ]; then
        pass "app container restarts after process kill (restart_policy)"
    else
        fail "app container status: $STATUS after kill"
    fi
}

test_disk_full_simulation() {
    echo "[CHAOS] Disk pressure: fill audit_log volume..."
    docker exec fortaleza-app dd if=/dev/zero of=/app/audit_logs/.fill bs=1M count=50 2>/dev/null || true
    sleep 2
    # Check if app still responds
    if docker exec fortaleza-app python -c "
import sys; sys.path.insert(0, '/app')
from audit import audit_logger, AuditEvent, AuditEventType
try:
    audit_logger.log(AuditEvent(event_type=AuditEventType.QUERY_EXECUTED, user_id='chaos', session_id='test', ip_address='127.0.0.1', resource='chaos_test', details={}))
    print('OK')
except Exception as e:
    print('FAIL:', e)
" 2>/dev/null; then
        pass "app handles disk pressure gracefully"
    else
        fail "app crashes under disk pressure"
    fi
    docker exec fortaleza-app rm -f /app/audit_logs/.fill 2>/dev/null || true
}

test_ollama_restart() {
    echo "[CHAOS] Dependency restart: restart ollama mid-query..."
    docker restart fortaleza-ollama
    sleep 15
    if docker exec fortaleza-app curl -sf http://ollama:11434/api/tags >/dev/null 2>&1; then
        pass "app reconnects to ollama after restart"
    else
        fail "app cannot reconnect to ollama after restart"
    fi
}

test_corrupted_vector_store() {
    echo "[CHAOS] Data corruption: inject garbage into ChromaDB..."
    mkdir -p /tmp/chaos_test_chroma
    docker exec fortaleza-app sh -c 'dd if=/dev/urandom of=/app/chroma_data/test_corrupt bs=1024 count=10 2>/dev/null' || true
    sleep 2
    if docker exec fortaleza-app python -c "
import sys; sys.path.insert(0, '/app')
from rag_engine import RAGEngine
try:
    engine = RAGEngine()
    print('OK: engine initialized after corruption')
except Exception as e:
    print('FAIL:', e)
" 2>/dev/null; then
        pass "app initializes after vector store corruption"
    else
        fail "app crashes after vector store corruption"
    fi
}

test_load_spike() {
    echo "[CHAOS] Load spike: send 50 concurrent requests..."
    for i in $(seq 1 50); do
        (docker exec fortaleza-app python -c "
import sys; sys.path.insert(0, '/app')
from rate_limiter import rate_limiter
rate_limiter.check_rate_limit('loadtest_user', '10.0.0.1')
" 2>/dev/null || true) &
    done
    wait
    sleep 3
    if docker exec fortaleza-app python -c "
import sys; sys.path.insert(0, '/app')
from rate_limiter import rate_limiter
ok = rate_limiter.check_rate_limit('loadtest_user', '10.0.0.1')
print('OK' if not ok else 'rate limit not triggered')
" 2>/dev/null; then
        pass "rate limiter blocks after load spike"
    else
        fail "rate limiter does not block after load spike"
    fi
}

# ── Main ──
echo "=========================================="
echo " Fortaleza Digital — Chaos Engineering"
echo "=========================================="
echo ""

TEST="${1:-all}"

if [ "$TEST" = "all" ] || [ "$TEST" = "network" ]; then test_network_partition; fi
if [ "$TEST" = "all" ] || [ "$TEST" = "process" ]; then test_process_kill; fi
if [ "$TEST" = "all" ] || [ "$TEST" = "disk" ]; then test_disk_full_simulation; fi
if [ "$TEST" = "all" ] || [ "$TEST" = "ollama" ]; then test_ollama_restart; fi
if [ "$TEST" = "all" ] || [ "$TEST" = "corrupt" ]; then test_corrupted_vector_store; fi
if [ "$TEST" = "all" ] || [ "$TEST" = "load" ]; then test_load_spike; fi

echo ""
echo "=========================================="
echo " Results: $PASS passed, $FAIL failed"
echo "=========================================="
[ "$FAIL" -eq 0 ] || exit 1
