"""
Unit tests for the immutable audit logging module.
Tests chain integrity, event logging, and tamper detection.
"""

import os
import sys
import json
import tempfile
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "app"))

from audit import AuditLogger, AuditEvent, AuditEventType


class TestAuditLogger:
    @pytest.fixture
    def audit_logger(self, tmpdir):
        os.environ["FORTALEZA_AUDIT_HMAC_KEY"] = "test-hmac-key-32chars-long!!"
        logger = AuditLogger(log_dir=str(tmpdir))
        return logger

    def test_log_event_creates_entry(self, audit_logger):
        event = AuditEvent(
            event_type=AuditEventType.LOGIN_SUCCESS,
            user_id="testuser",
            session_id="sess_001",
            ip_address="192.168.1.1",
            resource="auth.login",
            details={"method": "password"},
        )
        audit_logger.log(event)
        assert os.path.exists(audit_logger.log_file)

    def test_log_event_has_hash_chain(self, audit_logger):
        event1 = AuditEvent(
            event_type=AuditEventType.LOGIN_SUCCESS,
            user_id="user1", session_id="s1", ip_address="10.0.0.1",
            resource="auth.login", details={},
        )
        event2 = AuditEvent(
            event_type=AuditEventType.QUERY_EXECUTED,
            user_id="user1", session_id="s1", ip_address="10.0.0.1",
            resource="rag.query", details={"question": "test"},
        )
        audit_logger.log(event1)
        audit_logger.log(event2)
        assert event1.hash != event2.hash
        assert event2.previous_hash == event1.hash

    def test_verify_chain_valid(self, audit_logger):
        for i in range(5):
            audit_logger.log(AuditEvent(
                event_type=AuditEventType.SYSTEM_STARTUP,
                user_id="system", session_id="boot", ip_address="127.0.0.1",
                resource="system.boot", details={"iteration": i},
            ))
        assert audit_logger.verify_chain() is True

    def test_verify_chain_detects_tampering(self, audit_logger):
        audit_logger.log(AuditEvent(
            event_type=AuditEventType.SYSTEM_STARTUP,
            user_id="system", session_id="boot", ip_address="127.0.0.1",
            resource="system.boot", details={},
        ))
        with open(audit_logger.log_file, "a") as f:
            f.write('{"tampered": true}\n')
        assert audit_logger.verify_chain() is False

    def test_verify_chain_detects_modified_entry(self, audit_logger):
        audit_logger.log(AuditEvent(
            event_type=AuditEventType.DOCUMENT_INGESTED,
            user_id="admin", session_id="s1", ip_address="10.0.0.1",
            resource="ingest", details={"file": "doc.pdf"},
        ))
        with open(audit_logger.log_file, "r") as f:
            content = f.read()
        modified = content.replace("admin", "attacker")
        with open(audit_logger.log_file, "w") as f:
            f.write(modified)
        assert audit_logger.verify_chain() is False

    def test_query_returns_filtered_results(self, audit_logger):
        audit_logger.log(AuditEvent(
            event_type=AuditEventType.LOGIN_SUCCESS,
            user_id="alice", session_id="s1", ip_address="10.0.0.1",
            resource="auth.login", details={},
        ))
        audit_logger.log(AuditEvent(
            event_type=AuditEventType.LOGIN_FAILURE,
            user_id="bob", session_id="s2", ip_address="10.0.0.2",
            resource="auth.login", details={"reason": "bad password"},
        ))
        results = audit_logger.query(event_type=AuditEventType.LOGIN_FAILURE)
        assert len(results) == 1
        assert results[0]["user_id"] == "bob"

    def test_query_user_filter(self, audit_logger):
        audit_logger.log(AuditEvent(
            event_type=AuditEventType.LOGIN_SUCCESS,
            user_id="alice", session_id="s1", ip_address="10.0.0.1",
            resource="auth.login", details={},
        ))
        audit_logger.log(AuditEvent(
            event_type=AuditEventType.LOGIN_SUCCESS,
            user_id="bob", session_id="s2", ip_address="10.0.0.2",
            resource="auth.login", details={},
        ))
        results = audit_logger.query(user_id="alice")
        assert len(results) == 1

    def test_empty_log_verifies(self, audit_logger):
        assert audit_logger.verify_chain() is True

    def test_multiple_event_types(self, audit_logger):
        types = [
            AuditEventType.LOGIN_SUCCESS,
            AuditEventType.QUERY_EXECUTED,
            AuditEventType.DOCUMENT_INGESTED,
            AuditEventType.DATABASE_PURGED,
            AuditEventType.SYSTEM_SHUTDOWN,
        ]
        for t in types:
            audit_logger.log(AuditEvent(
                event_type=t, user_id="admin", session_id="s1",
                ip_address="10.0.0.1", resource="test", details={},
            ))
        assert audit_logger.verify_chain() is True
