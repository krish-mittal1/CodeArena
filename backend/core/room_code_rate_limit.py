"""
Rate limiting for private room code enumeration attacks.

Prevents brute force attacks on room codes by limiting:
- Requests per IP per minute
- Invalid code attempts per IP
"""

from __future__ import annotations

import time
from collections import deque
from threading import Lock

from backend.core.exceptions import RoomCodeRateLimited

_WINDOW_SECONDS = 60
_MAX_ATTEMPTS = 20  # Conservative limit to prevent enumeration
_entries: dict[str, deque[float]] = {}
_lock = Lock()


def _prune(now: float, attempts: deque[float]) -> None:
    """Remove old attempts outside the rate limit window."""
    cutoff = now - _WINDOW_SECONDS
    while attempts and attempts[0] < cutoff:
        attempts.popleft()


def _key(ip: str) -> str:
    """Create a rate limit key for an IP address."""
    return f"room_code|{ip}"


def ensure_room_code_allowed(ip: str) -> None:
    """
    Raise if room code requests exceed the threshold.
    This blocks enumeration/brute force attempts.
    """
    now = time.monotonic()
    entry_key = _key(ip)

    with _lock:
        attempts = _entries.get(entry_key)
        if attempts:
            _prune(now, attempts)
            if len(attempts) >= _MAX_ATTEMPTS:
                raise RoomCodeRateLimited()
            if not attempts:
                _entries.pop(entry_key, None)


def record_room_code_attempt(ip: str) -> None:
    """Record a room code attempt for rate limiting."""
    now = time.monotonic()
    entry_key = _key(ip)

    with _lock:
        attempts = _entries.setdefault(entry_key, deque())
        _prune(now, attempts)
        attempts.append(now)
