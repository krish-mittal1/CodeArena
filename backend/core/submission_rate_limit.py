"""
Rate limiting for code submissions.

Uses Redis sorted-set rolling windows when Redis is available (multi-instance
safe). Falls back to in-memory deques when redis is None (dev mode).
"""

from __future__ import annotations

import time
import uuid
from collections import deque
from threading import Lock
from typing import Optional

from redis.asyncio import Redis

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


def _redis_key(user_id: str, match_id: str) -> str:
    return f"ratelimit:submit:{user_id}:{match_id}"


_last_full_prune: float = 0.0
_FULL_PRUNE_INTERVAL = 60.0


async def ensure_submission_allowed(
    user_id: str,
    match_id: str,
    redis: Optional[Redis] = None,
) -> None:
    """Raise if submissions exceed the short rolling window threshold."""
    if redis is not None:
        key = _redis_key(user_id, match_id)
        now = time.time()
        pipe = redis.pipeline()
        pipe.zremrangebyscore(key, 0, now - _WINDOW_SECONDS)
        pipe.zcard(key)
        _, count = await pipe.execute()
        if int(count) >= _MAX_SUBMISSIONS:
            raise SubmissionRateLimited()
        return

    global _last_full_prune
    now = time.monotonic()
    entry_key = _key(user_id, match_id)

    with _lock:
        if now - _last_full_prune > _FULL_PRUNE_INTERVAL:
            _last_full_prune = now
            stale = [k for k, v in _entries.items() if not v or v[-1] < now - _WINDOW_SECONDS]
            for k in stale:
                del _entries[k]

        attempts = _entries.get(entry_key)
        if attempts:
            _prune(now, attempts)
            if len(attempts) >= _MAX_SUBMISSIONS:
                raise SubmissionRateLimited()
            if not attempts:
                _entries.pop(entry_key, None)


async def record_submission(
    user_id: str,
    match_id: str,
    redis: Optional[Redis] = None,
) -> None:
    """Record a successful submission request for throttling."""
    if redis is not None:
        key = _redis_key(user_id, match_id)
        now = time.time()
        member = f"{now}:{uuid.uuid4().hex[:8]}"
        pipe = redis.pipeline()
        pipe.zadd(key, {member: now})
        pipe.expire(key, _WINDOW_SECONDS + 1)
        await pipe.execute()
        return

    now = time.monotonic()
    entry_key = _key(user_id, match_id)

    with _lock:
        attempts = _entries.setdefault(entry_key, deque())
        _prune(now, attempts)
        attempts.append(now)
