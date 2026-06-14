"""
Input validation and sanitization for user queries.
Prevents injection, excessive length, and malformed input.
"""

import re
import logging
from typing import Tuple, Optional

logger = logging.getLogger(__name__)

MAX_QUERY_LENGTH = 2000
MIN_QUERY_LENGTH = 1
BLOCKED_PATTERNS = [
    r"(?i)\bignore\s+(all\s+)?previous\s+instructions\b",
    r"(?i)\bforget\s+(everything|all)\b",
    r"(?i)\byou\s+are\s+(now\s+)?a\s+(free|unconstrained|jailbroken)\b",
    r"(?i)\bDAN\b",
    r"(?i)\b(ST|DE|SYSTEM)\s*(:|:)\s*(PROMPT|MESSAGE|INSTRUCTION)\b",
    r"(?i)\[system\]",
    r"(?i)<\|[^|]+\|>",
    r"(?i)\b(reveal|output|print|show|display)\s+(the\s+)?(system\s+)?(prompt|instructions)\b",
]


def validate_query(query: str) -> Tuple[bool, str]:
    """
    Validate a user query before processing.
    
    Returns:
        Tuple of (is_valid, error_message_or_empty_string)
    """
    if not query or not query.strip():
        return False, "La consulta no puede estar vacia."

    stripped = query.strip()

    if len(stripped) > MAX_QUERY_LENGTH:
        return False, f"La consulta excede el limite de {MAX_QUERY_LENGTH} caracteres."

    if len(stripped) < MIN_QUERY_LENGTH:
        return False, "La consulta debe contener al menos un caracter."

    for pattern in COMPILED_PATTERNS:
        if pattern.search(stripped):
            logger.warning(f"Query blocked by pattern: {pattern.pattern[:50]}")
            return False, "La consulta contiene patrones no permitidos."

    return True, ""


COMPILED_PATTERNS = [re.compile(p) for p in BLOCKED_PATTERNS]


def sanitize_query(query: str) -> str:
    """Strip dangerous characters from query while preserving meaning."""
    sanitized = query.strip()
    sanitized = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F]", "", sanitized)
    return sanitized[:MAX_QUERY_LENGTH]
