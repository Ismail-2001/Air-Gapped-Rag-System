"""
Rate limiting middleware for Fortaleza Digital.
Tracks request frequency per user and enforces limits.
"""

import os
import time
import logging
import threading
from typing import Dict, Tuple
from collections import defaultdict

logger = logging.getLogger(__name__)

DEFAULT_MAX_REQUESTS = 30
DEFAULT_WINDOW_SECONDS = 60


class RateLimiter:
    """
    Sliding window rate limiter per user.
    Tracks query counts in a configurable time window.
    """

    def __init__(self, max_requests: int = None, window_seconds: int = None):
        self.max_requests = max_requests or int(os.getenv("FORTALEZA_RATE_LIMIT", str(DEFAULT_MAX_REQUESTS)))
        self.window_seconds = window_seconds or int(os.getenv("FORTALEZA_RATE_WINDOW", str(DEFAULT_WINDOW_SECONDS)))
        self._buckets: Dict[str, list] = defaultdict(list)
        self._lock = threading.Lock()

    def check(self, user_id: str) -> Tuple[bool, int]:
        """
        Check if request is allowed for the given user.

        Returns:
            Tuple of (allowed, remaining_requests_in_window)
        """
        now = time.time()
        window_start = now - self.window_seconds

        with self._lock:
            timestamps = self._buckets[user_id]
            timestamps[:] = [t for t in timestamps if t > window_start]

            if len(timestamps) >= self.max_requests:
                remaining = 0
                retry_after = int(timestamps[0] + self.window_seconds - now)
                logger.warning(f"Rate limit exceeded for user '{user_id}'. Retry after {retry_after}s.")
                return False, retry_after

            timestamps.append(now)
            remaining = self.max_requests - len(timestamps)

        return True, remaining

    def get_remaining(self, user_id: str) -> int:
        """Get remaining requests for user without consuming a slot."""
        now = time.time()
        window_start = now - self.window_seconds

        with self._lock:
            timestamps = self._buckets.get(user_id, [])
            timestamps[:] = [t for t in timestamps if t > window_start]
            remaining = self.max_requests - len(timestamps)

        return max(0, remaining)


rate_limiter = RateLimiter()
