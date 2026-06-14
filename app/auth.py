"""
Authentication and Authorization Module for Fortaleza Digital.
Provides JWT-based authentication with RBAC and clearance levels.
Supports local password auth and SSO via OpenID Connect.
"""

import os
import hmac
import hashlib
import json
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class ClearanceLevel(Enum):
    UNCLASSIFIED = 0
    CONFIDENTIAL = 1
    SECRET = 2
    TOP_SECRET = 3
    COSMIC_TOP_SECRET = 4


class Role(Enum):
    OPERATOR = "operator"
    ANALYST = "analyst"
    INGESTOR = "ingestor"
    ADMIN = "admin"
    AUDITOR = "auditor"
    SRE = "sre"
    SUPER_ADMIN = "super_admin"


ROLE_HIERARCHY = {
    Role.OPERATOR: 0,
    Role.ANALYST: 1,
    Role.INGESTOR: 2,
    Role.ADMIN: 3,
    Role.AUDITOR: 3,
    Role.SRE: 3,
    Role.SUPER_ADMIN: 4,
}


@dataclass
class User:
    username: str
    role: Role
    clearance: ClearanceLevel
    hashed_password: str
    display_name: str = ""
    organization: str = ""
    enabled: bool = True
    last_login: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)

    def can_access(self, document_clearance: ClearanceLevel) -> bool:
        return self.clearance.value >= document_clearance.value

    def has_permission(self, required_role: Role) -> bool:
        return ROLE_HIERARCHY.get(self.role, -1) >= ROLE_HIERARCHY.get(required_role, -1)


class AuthManager:
    def __init__(self):
        self.secret_key = os.getenv("FORTALEZA_JWT_SECRET", hashlib.sha256(os.urandom(64)).hexdigest())
        self.session_ttl = int(os.getenv("FORTALEZA_SESSION_TTL", "480"))
        self.auth_mode = os.getenv("FORTALEZA_AUTH_MODE", "local")
        self._users: Dict[str, User] = {}
        self._load_users()

    def _load_users(self):
        users_json = os.getenv("FORTALEZA_USERS", "{}")
        try:
            users_dict = json.loads(users_json)
            for username, user_data in users_dict.items():
                self._users[username] = User(
                    username=username,
                    role=Role(user_data.get("role", "operator")),
                    clearance=ClearanceLevel[user_data.get("clearance", "UNCLASSIFIED").upper()],
                    hashed_password=user_data["hashed_password"],
                    display_name=user_data.get("display_name", username),
                    organization=user_data.get("organization", ""),
                )
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to load users: {e}")
        if not self._users:
            default_pass = os.getenv("FORTALEZA_ADMIN_PASSWORD", "admin")
            self._users["admin"] = User(
                username="admin",
                role=Role.SUPER_ADMIN,
                clearance=ClearanceLevel.TOP_SECRET,
                hashed_password=self._hash_password(default_pass),
                display_name="System Administrator",
            )
            logger.warning("No users configured. Created default 'admin' user. CHANGE PASSWORD IMMEDIATELY.")

    def _hash_password(self, password: str) -> str:
        salt = os.urandom(32)
        key = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 600000)
        return salt.hex() + ":" + key.hex()

    def verify_password(self, password: str, stored: str) -> bool:
        try:
            salt_hex, key_hex = stored.split(":")
            salt = bytes.fromhex(salt_hex)
            expected_key = bytes.fromhex(key_hex)
            actual_key = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 600000)
            return hmac.compare_digest(actual_key, expected_key)
        except (ValueError, AttributeError):
            return False

    def authenticate(self, username: str, password: str, ip: str = "0.0.0.0") -> Optional[str]:
        user = self._users.get(username)
        if not user or not user.enabled:
            logger.warning(f"Login attempt for unknown/disabled user: {username} from {ip}")
            return None
        if not self.verify_password(password, user.hashed_password):
            logger.warning(f"Failed login for user: {username} from {ip}")
            return None
        user.last_login = datetime.utcnow()
        token = self._create_token(user)
        logger.info(f"User '{username}' authenticated successfully from {ip}.")
        return token

    def _create_token(self, user: User) -> str:
        header = {"alg": "HS256", "typ": "JWT"}
        payload = {
            "sub": user.username,
            "role": user.role.value,
            "clearance": user.clearance.name,
            "iat": int(datetime.utcnow().timestamp()),
            "exp": int((datetime.utcnow() + timedelta(minutes=self.session_ttl)).timestamp()),
            "jti": hashlib.sha256(os.urandom(32)).hexdigest()[:16],
        }
        header_b64 = self._b64encode(json.dumps(header).encode())
        payload_b64 = self._b64encode(json.dumps(payload).encode())
        signature = hmac.new(
            self.secret_key.encode(),
            f"{header_b64}.{payload_b64}".encode(),
            hashlib.sha256,
        ).digest()
        sig_b64 = self._b64encode(signature)
        return f"{header_b64}.{payload_b64}.{sig_b64}"

    def _b64encode(self, data: bytes) -> str:
        import base64
        return base64.urlsafe_b64encode(data).rstrip(b"=").decode()

    def _b64decode(self, data: str) -> bytes:
        import base64
        padding = 4 - len(data) % 4
        if padding != 4:
            data += "=" * padding
        return base64.urlsafe_b64decode(data)

    def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        try:
            parts = token.split(".")
            if len(parts) != 3:
                return None
            header_b64, payload_b64, sig_b64 = parts
            expected_sig = hmac.new(
                self.secret_key.encode(),
                f"{header_b64}.{payload_b64}".encode(),
                hashlib.sha256,
            ).digest()
            actual_sig = self._b64decode(sig_b64)
            if not hmac.compare_digest(actual_sig, expected_sig):
                return None
            payload = json.loads(self._b64decode(payload_b64))
            if payload.get("exp", 0) < datetime.utcnow().timestamp():
                logger.warning("Expired token used.")
                return None
            return payload
        except Exception as e:
            logger.warning(f"Invalid token: {e}")
            return None

    def get_user(self, username: str) -> Optional[User]:
        return self._users.get(username)


auth_manager = AuthManager()
