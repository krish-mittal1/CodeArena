"""
Conservative in-memory rate limiting for password auth endpoints.

This is intentionally lightweight and single-instance friendly so it can be
enabled without any database or Redis dependency changes.
"""

from __future__ import annotations

import time
from collections import deque
from threading import Lock

from backend.core.exceptions import LoginRateLimited

_WINDOW_SECONDS = 15 * 60
_MAX_FAILED_ATTEMPTS = 10
_entries: dict[str, deque[float]] = {}
_lock = Lock()


def _prune(now: float, attempts: deque[float]) -> None:
    cutoff = now - _WINDOW_SECONDS
    while attempts and attempts[0] < cutoff:
        attempts.popleft()


def _key(*parts: str) -> str:
    return "|".join((part or "").strip().lower() for part in parts)


_last_full_prune: float = 0.0
_FULL_PRUNE_INTERVAL = 300.0


def _full_prune_if_needed(now: float) -> None:
    global _last_full_prune
    if now - _last_full_prune < _FULL_PRUNE_INTERVAL:
        return
    _last_full_prune = now
    stale = [k for k, v in _entries.items() if not v or v[-1] < now - _WINDOW_SECONDS]
    for k in stale:
        del _entries[k]


def ensure_login_allowed(username: str, ip: str) -> None:
    """
    Raise if recent failed attempts for this username/IP combination exceed
    the threshold. This only counts failures, so normal users are unaffected.
    """
    now = time.monotonic()
    candidate_keys = (
        _key("login", "user", username),
        _key("login", "ip", ip),
        _key("login", "pair", username, ip),
    )

    with _lock:
        _full_prune_if_needed(now)
        for entry_key in candidate_keys:
            attempts = _entries.get(entry_key)
            if not attempts:
                continue
            _prune(now, attempts)
            if len(attempts) >= _MAX_FAILED_ATTEMPTS:
                raise LoginRateLimited()
            if not attempts:
                _entries.pop(entry_key, None)


def record_login_failure(username: str, ip: str) -> None:
    now = time.monotonic()
    failure_keys = (
        _key("login", "user", username),
        _key("login", "ip", ip),
        _key("login", "pair", username, ip),
    )

    with _lock:
        for entry_key in failure_keys:
            attempts = _entries.setdefault(entry_key, deque())
            _prune(now, attempts)
            attempts.append(now)


def clear_login_failures(username: str, ip: str) -> None:
    success_keys = (
        _key("login", "user", username),
        _key("login", "ip", ip),
        _key("login", "pair", username, ip),
    )

    with _lock:
        for entry_key in success_keys:
            _entries.pop(entry_key, None)
