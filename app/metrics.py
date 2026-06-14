"""Prometheus metrics and OpenTelemetry tracing for Fortaleza Digital."""

import os
import time
import logging
from functools import wraps
from typing import Callable, Any

from config import config

try:
    from prometheus_client import Counter, Histogram, Gauge, generate_latest, REGISTRY, start_http_server
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

logger = logging.getLogger(__name__)

# ── Prometheus Metrics ──
if PROMETHEUS_AVAILABLE:
    QUERY_COUNT = Counter("fortaleza_queries_total", "Total RAG queries",
                          ["status", "user_role"])
    QUERY_LATENCY = Histogram("fortaleza_query_latency_seconds",
                               "Query end-to-end latency",
                               buckets=[0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0])
    DOCUMENT_INGEST_COUNT = Counter("fortaleza_documents_ingested_total",
                                   "Documents ingested", ["source"])
    ERROR_COUNT = Counter("fortaleza_errors_total", "Total errors",
                          ["component", "type"])
    ACTIVE_SESSIONS = Gauge("fortaleza_active_sessions", "Active user sessions")
    VECTOR_STORE_SIZE = Gauge("fortaleza_vector_store_documents",
                              "Number of documents in vector store")
    RERANKER_LATENCY = Histogram("fortaleza_reranker_latency_seconds",
                                  "Cross-encoder reranking latency",
                                  buckets=[0.05, 0.1, 0.25, 0.5, 1.0, 2.0])
    LLM_LATENCY = Histogram("fortaleza_llm_latency_seconds",
                             "LLM generation latency",
                             buckets=[0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0])
else:
    class _NoopMetric:
        def labels(self, **kwargs): return self
        def inc(self, amount=1): pass
        def observe(self, amount): pass
        def set(self, value): pass
    QUERY_COUNT = QUERY_LATENCY = DOCUMENT_INGEST_COUNT = _NoopMetric()
    ERROR_COUNT = ACTIVE_SESSIONS = VECTOR_STORE_SIZE = _NoopMetric()
    RERANKER_LATENCY = LLM_LATENCY = _NoopMetric()


def observe_query(func: Callable) -> Callable:
    """Decorator that records query latency and counts."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.monotonic()
        try:
            result = func(*args, **kwargs)
            latency = time.monotonic() - start
            QUERY_LATENCY.observe(latency)
            role = kwargs.get("user", "anonymous")
            QUERY_COUNT.labels(status="success", user_role=role).inc()
            return result
        except Exception as e:
            latency = time.monotonic() - start
            QUERY_LATENCY.observe(latency)
            QUERY_COUNT.labels(status="error", user_role="unknown").inc()
            ERROR_COUNT.labels(component="rag_engine", type=type(e).__name__).inc()
            raise
    return wrapper


def observe_llm(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.monotonic()
        try:
            result = func(*args, **kwargs)
            LLM_LATENCY.observe(time.monotonic() - start)
            return result
        except Exception:
            LLM_LATENCY.observe(time.monotonic() - start)
            raise
    return wrapper


def observe_reranker(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.monotonic()
        try:
            result = func(*args, **kwargs)
            RERANKER_LATENCY.observe(time.monotonic() - start)
            return result
        except Exception:
            RERANKER_LATENCY.observe(time.monotonic() - start)
            raise
    return wrapper


def metrics_endpoint() -> bytes:
    """Return Prometheus metrics in text format."""
    return generate_latest(REGISTRY)


def start_metrics_server(port: int = 8000) -> None:
    """Start Prometheus HTTP server in a background thread."""
    if PROMETHEUS_AVAILABLE:
        try:
            start_http_server(port)
            logger.info("Metrics server started on port %d", port)
        except Exception as e:
            logger.warning("Metrics server failed on port %d: %s", port, e)
    else:
        logger.info("prometheus_client not installed, metrics disabled")
