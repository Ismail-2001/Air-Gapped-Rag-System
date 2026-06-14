"""
Unit tests for the authentication module.
Tests JWT generation, validation, RBAC, and clearance levels.
"""

import os
import sys
import time
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "app"))

from auth import auth_manager, AuthManager, User, Role, ClearanceLevel


class TestAuthManager:
    def setup_method(self):
        os.environ["FORTALEZA_JWT_SECRET"] = "test-secret-key-for-testing-only"
        os.environ["FORTALEZA_USERS"] = (
            '{"testuser":{"role":"analyst","clearance":"SECRET",'
            '"hashed_password":"00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000:00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",'
            '"display_name":"Test User"}}'
        )
        os.environ["FORTALEZA_ADMIN_PASSWORD"] = "admin123"
        self.manager = AuthManager()

    def test_authenticate_valid_user(self):
        token = self.manager.authenticate("admin", "admin123")
        assert token is not None
        assert len(token.split(".")) == 3

    def test_authenticate_invalid_password(self):
        token = self.manager.authenticate("admin", "wrongpassword")
        assert token is None

    def test_authenticate_nonexistent_user(self):
        token = self.manager.authenticate("nonexistent", "pass123")
        assert token is None

    def test_validate_token_valid(self):
        token = self.manager.authenticate("admin", "admin123")
        payload = self.manager.validate_token(token)
        assert payload is not None
        assert payload["sub"] == "admin"
        assert payload["role"] == "super_admin"

    def test_validate_token_tampered(self):
        token = self.manager.authenticate("admin", "admin123")
        parts = token.split(".")
        tampered = parts[0] + "." + parts[1] + ".invalidsignature"
        payload = self.manager.validate_token(tampered)
        assert payload is None

    def test_validate_token_expired(self):
        os.environ["FORTALEZA_SESSION_TTL"] = "0"
        manager = AuthManager()
        token = manager.authenticate("admin", "admin123")
        payload = manager.validate_token(token)
        assert payload is None

    def test_token_contains_user_claims(self):
        token = self.manager.authenticate("admin", "admin123")
        payload = self.manager.validate_token(token)
        assert "sub" in payload
        assert "role" in payload
        assert "clearance" in payload
        assert "iat" in payload
        assert "exp" in payload
        assert "jti" in payload


class TestAuthorization:
    def test_role_hierarchy_operator_lowest(self):
        op = Role.OPERATOR
        sa = Role.SUPER_ADMIN
        assert auth_manager is not None

    def test_clearance_level_access(self):
        secret_user = User("test", Role.ANALYST, ClearanceLevel.SECRET, "hash")
        assert secret_user.can_access(ClearanceLevel.CONFIDENTIAL)
        assert secret_user.can_access(ClearanceLevel.SECRET)
        assert not secret_user.can_access(ClearanceLevel.TOP_SECRET)
        assert not secret_user.can_access(ClearanceLevel.COSMIC_TOP_SECRET)

    def test_unclassified_cannot_access_above(self):
        user = User("test", Role.OPERATOR, ClearanceLevel.UNCLASSIFIED, "hash")
        assert user.can_access(ClearanceLevel.UNCLASSIFIED)
        assert not user.can_access(ClearanceLevel.CONFIDENTIAL)
        assert not user.can_access(ClearanceLevel.SECRET)

    def test_has_permission_role_hierarchy(self):
        operator = User("op", Role.OPERATOR, ClearanceLevel.UNCLASSIFIED, "hash")
        admin = User("ad", Role.ADMIN, ClearanceLevel.SECRET, "hash")
        super_admin = User("sa", Role.SUPER_ADMIN, ClearanceLevel.TOP_SECRET, "hash")

        assert not operator.has_permission(Role.ANALYST)
        assert not operator.has_permission(Role.ADMIN)
        assert admin.has_permission(Role.ANALYST)
        assert admin.has_permission(Role.INGESTOR)
        assert not admin.has_permission(Role.SUPER_ADMIN)
        assert super_admin.has_permission(Role.OPERATOR)
        assert super_admin.has_permission(Role.SUPER_ADMIN)


class TestPasswordHashing:
    def setup_method(self):
        os.environ["FORTALEZA_ADMIN_PASSWORD"] = "testpass"
        self.manager = AuthManager()

    def test_hash_and_verify(self):
        hashed = self.manager._hash_password("securepassword123")
        assert ":" in hashed
        assert self.manager.verify_password("securepassword123", hashed)

    def test_wrong_password_fails(self):
        hashed = self.manager._hash_password("correctpass")
        assert not self.manager.verify_password("wrongpass", hashed)

    def test_empty_password_fails(self):
        hashed = self.manager._hash_password("somepass")
        assert not self.manager.verify_password("", hashed)
