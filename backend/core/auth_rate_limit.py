"""
Rate limiting for password / OTP auth endpoints.

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


def _redis_key(*parts: str) -> str:
    return "ratelimit:" + _key(*parts)


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


def _candidate_keys(username: str, ip: str) -> tuple[str, str, str]:
    return (
        _key("login", "user", username),
        _key("login", "ip", ip),
        _key("login", "pair", username, ip),
    )


async def ensure_login_allowed(
    username: str,
    ip: str,
    redis: Optional[Redis] = None,
) -> None:
    """
    Raise if recent failed attempts for this username/IP combination exceed
    the threshold. This only counts failures, so normal users are unaffected.
    """
    if redis is not None:
        now = time.time()
        for entry_key in _candidate_keys(username, ip):
            key = _redis_key(entry_key)
            pipe = redis.pipeline()
            pipe.zremrangebyscore(key, 0, now - _WINDOW_SECONDS)
            pipe.zcard(key)
            _, count = await pipe.execute()
            if int(count) >= _MAX_FAILED_ATTEMPTS:
                raise LoginRateLimited()
        return

    now = time.monotonic()
    candidate_keys = _candidate_keys(username, ip)

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


async def record_login_failure(
    username: str,
    ip: str,
    redis: Optional[Redis] = None,
) -> None:
    if redis is not None:
        now = time.time()
        member = f"{now}:{uuid.uuid4().hex[:8]}"
        pipe = redis.pipeline()
        for entry_key in _candidate_keys(username, ip):
            key = _redis_key(entry_key)
            pipe.zadd(key, {member: now})
            pipe.expire(key, _WINDOW_SECONDS + 1)
        await pipe.execute()
        return

    now = time.monotonic()
    failure_keys = _candidate_keys(username, ip)

    with _lock:
        for entry_key in failure_keys:
            attempts = _entries.setdefault(entry_key, deque())
            _prune(now, attempts)
            attempts.append(now)


async def clear_login_failures(
    username: str,
    ip: str,
    redis: Optional[Redis] = None,
) -> None:
    success_keys = _candidate_keys(username, ip)

    if redis is not None:
        await redis.delete(*(_redis_key(k) for k in success_keys))
        return

    with _lock:
        for entry_key in success_keys:
            _entries.pop(entry_key, None)
