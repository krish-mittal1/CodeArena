"""
Conservative in-memory rate limiting for code submissions.

Goal: reduce accidental or abusive submission spam while minimizing impact
on normal users. This is intentionally lightweight and single-instance only.
"""

from __future__ import annotations

import time
from collections import deque
from threading import Lock

from backend.core.exceptions import SubmissionRateLimited

_WINDOW_SECONDS = 5
_MAX_SUBMISSIONS = 3
_entries: dict[str, deque[float]] = {}
_lock = Lock()


def _prune(now: float, attempts: deque[float]) -> None:
    cutoff = now - _WINDOW_SECONDS
    while attempts and attempts[0] < cutoff:
        attempts.popleft()


def _key(user_id: str, match_id: str) -> str:
    return f"submit|{user_id}|{match_id}"


def ensure_submission_allowed(user_id: str, match_id: str) -> None:
    """Raise if submissions exceed the short rolling window threshold."""
    now = time.monotonic()
    entry_key = _key(user_id, match_id)

    with _lock:
        attempts = _entries.get(entry_key)
        if attempts:
            _prune(now, attempts)
            if len(attempts) >= _MAX_SUBMISSIONS:
                raise SubmissionRateLimited()
            if not attempts:
                _entries.pop(entry_key, None)


def record_submission(user_id: str, match_id: str) -> None:
    """Record a successful submission request for throttling."""
    now = time.monotonic()
    entry_key = _key(user_id, match_id)

    with _lock:
        attempts = _entries.setdefault(entry_key, deque())
        _prune(now, attempts)
        attempts.append(now)
