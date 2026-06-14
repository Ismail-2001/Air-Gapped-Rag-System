"""
Immutable audit logging system for Fortaleza Digital.
Logs are written to an append-only, integrity-verified store.
Tampering with any entry breaks all subsequent hashes in the chain.
"""

import os
import json
import hmac
import hashlib
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)


class AuditEventType(Enum):
    LOGIN_SUCCESS = "login.success"
    LOGIN_FAILURE = "login.failure"
    LOGOUT = "logout"
    QUERY_EXECUTED = "query.executed"
    QUERY_FAILED = "query.failed"
    DOCUMENT_INGESTED = "document.ingested"
    DOCUMENT_INGEST_FAILED = "document.ingest_failed"
    DATABASE_PURGED = "database.purged"
    USER_CREATED = "user.created"
    USER_DISABLED = "user.disabled"
    PERMISSION_CHANGED = "permission.changed"
    SYSTEM_STARTUP = "system.startup"
    SYSTEM_SHUTDOWN = "system.shutdown"


@dataclass
class AuditEvent:
    event_type: AuditEventType
    user_id: str
    session_id: str
    ip_address: str
    resource: str
    details: Dict[str, Any]
    timestamp: str = ""
    event_id: str = ""
    previous_hash: str = ""
    hash: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()
        if not self.event_id:
            self.event_id = hashlib.sha256(os.urandom(32)).hexdigest()[:16]


class AuditLogger:
    """
    Append-only audit logger with chain integrity verification.
    Each entry contains the HMAC-SHA256 of the previous entry,
    creating an immutable chain.
    """

    def __init__(self, log_dir: str = "/app/audit_logs"):
        self.log_dir = log_dir
        self.log_file = os.path.join(log_dir, "audit.chain.log")
        self.integrity_file = os.path.join(log_dir, "audit.integrity")
        self.hmac_key = os.getenv("FORTALEZA_AUDIT_HMAC_KEY",
                                  hashlib.sha256(os.urandom(64)).hexdigest())
        self._ensure_log_dir()
        self._last_hash = self._load_last_hash()

    def _ensure_log_dir(self):
        os.makedirs(self.log_dir, exist_ok=True)
        if os.name == "posix":
            try:
                os.chmod(self.log_dir, 0o750)
            except PermissionError:
                pass

    def _load_last_hash(self) -> str:
        try:
            with open(self.integrity_file, "r") as f:
                return f.read().strip()
        except FileNotFoundError:
            return hashlib.sha256(b"genesis").hexdigest()

    def _save_last_hash(self, hash_value: str):
        with open(self.integrity_file, "w") as f:
            f.write(hash_value)
        if os.name == "posix":
            try:
                os.chmod(self.integrity_file, 0o440)
            except PermissionError:
                pass

    def _compute_hash(self, entry: str) -> str:
        message = f"{self._last_hash}|{entry}".encode()
        return hmac.new(
            self.hmac_key.encode(),
            message,
            hashlib.sha256
        ).hexdigest()

    def log(self, event: AuditEvent):
        event.previous_hash = self._last_hash
        entry_dict = asdict(event)
        entry_json = json.dumps(entry_dict, sort_keys=True, default=str)
        event.hash = self._compute_hash(entry_json)
        final_entry = json.dumps(asdict(event), sort_keys=True, default=str)

        try:
            with open(self.log_file, "a") as f:
                f.write(final_entry + "\n")
                f.flush()
                os.fsync(f.fileno())
            self._last_hash = event.hash
            self._save_last_hash(event.hash)
        except IOError as e:
            logger.error(f"Failed to write audit log: {e}")
            raise

    def verify_chain(self) -> bool:
        """Verify integrity of the entire audit chain."""
        try:
            with open(self.log_file, "r") as f:
                entries = f.readlines()
        except FileNotFoundError:
            return True

        previous_hash = hashlib.sha256(b"genesis").hexdigest()

        for entry in entries:
            entry = entry.strip()
            if not entry:
                continue
            try:
                data = json.loads(entry)
            except json.JSONDecodeError:
                logger.error("Corrupt audit entry detected.")
                return False

            stored_hash = data.get("hash", "")
            stored_prev_hash = data.get("previous_hash", "")

            if stored_prev_hash != previous_hash:
                logger.error(f"Chain break: expected prev_hash={previous_hash}, got={stored_prev_hash}")
                return False

            verify_data = {k: v for k, v in data.items() if k != "hash"}
            verify_json = json.dumps(verify_data, sort_keys=True, default=str)
            message = f"{previous_hash}|{verify_json}".encode()
            expected_hash = hmac.new(
                self.hmac_key.encode(), message, hashlib.sha256
            ).hexdigest()

            if expected_hash != stored_hash:
                logger.error(f"Hash mismatch at entry {verify_data.get('event_id', 'unknown')}")
                return False

            previous_hash = stored_hash

        stored_integrity = self._load_last_hash()
        if stored_integrity != previous_hash:
            logger.error("Integrity file does not match chain tail.")
            return False

        return True

    def query(self, limit: int = 100, offset: int = 0,
              event_type: Optional[AuditEventType] = None,
              user_id: Optional[str] = None,
              start_time: Optional[str] = None,
              end_time: Optional[str] = None) -> list:
        try:
            with open(self.log_file, "r") as f:
                entries = f.readlines()
        except FileNotFoundError:
            return []

        results = []
        for entry in entries:
            entry = entry.strip()
            if not entry:
                continue
            try:
                data = json.loads(entry)
            except json.JSONDecodeError:
                continue

            if event_type and data.get("event_type") != event_type.value:
                continue
            if user_id and data.get("user_id") != user_id:
                continue
            if start_time and data.get("timestamp", "") < start_time:
                continue
            if end_time and data.get("timestamp", "") > end_time:
                continue

            results.append(data)

        return results[offset:offset + limit]


audit_logger = AuditLogger()
