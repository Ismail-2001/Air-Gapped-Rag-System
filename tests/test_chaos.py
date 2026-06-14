"""Resilience and chaos engineering unit tests for Fortaleza Digital."""

import os
import sys
import time
import pytest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "app"))


class TestResiliencePatterns:
    """Tests that verify system resilience to failures."""

    def test_rate_limiter_recovers_after_window(self, mock_config):
        from rate_limiter import rate_limiter
        rate_limiter.max_requests = 3
        rate_limiter.window_seconds = 2
        for _ in range(3):
            rate_limiter.check_rate_limit("resilience-user", "10.0.0.1")
        blocked = rate_limiter.check_rate_limit("resilience-user", "10.0.0.1")
        assert blocked is False
        time.sleep(2.1)
        allowed = rate_limiter.check_rate_limit("resilience-user", "10.0.0.1")
        assert allowed is True

    def test_audit_chain_detects_tamper(self):
        from audit import audit_logger
        log = audit_logger.get_log(limit=1)
        if log:
            last = log[-1]
            with open(audit_logger.log_path, "r+b") as f:
                f.seek(-50, 2)
                f.write(b"TAMPER")
            verified = audit_logger.verify_chain()
            assert verified is False

    def test_jwt_expired_rejected(self):
        from auth import auth_manager
        import jwt, time
        payload = {
            "sub": "expired_user",
            "role": "viewer",
            "clearance": 1,
            "exp": int(time.time()) - 3600,
        }
        token = jwt.encode(payload, auth_manager.secret, algorithm="HS256")
        user = auth_manager.validate_token(token)
        assert user is None

    def test_invalid_jwt_signature_rejected(self):
        from auth import auth_manager
        import jwt, time
        payload = {
            "sub": "evil_user",
            "role": "superadmin",
            "clearance": 7,
            "exp": int(time.time()) + 3600,
        }
        token = jwt.encode(payload, "wrong-secret", algorithm="HS256")
        user = auth_manager.validate_token(token)
        assert user is None

    def test_empty_query_returns_empty(self):
        from input_validator import validate_query
        result = validate_query("")
        assert result["is_valid"] is False

    def test_very_long_query_truncated(self):
        from input_validator import validate_query
        long_q = "A" * 5000
        result = validate_query(long_q)
        assert len(result["sanitized_query"]) <= 2000
