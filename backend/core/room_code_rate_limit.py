"""
Rate limiting for private room code enumeration attacks.

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


def _redis_key(ip: str) -> str:
    return f"ratelimit:room_code:{ip}"


async def ensure_room_code_allowed(ip: str, redis: Optional[Redis] = None) -> None:
    """
    Raise if room code requests exceed the threshold.
    This blocks enumeration/brute force attempts.
    """
    if redis is not None:
        key = _redis_key(ip)
        now = time.time()
        pipe = redis.pipeline()
        pipe.zremrangebyscore(key, 0, now - _WINDOW_SECONDS)
        pipe.zcard(key)
        _, count = await pipe.execute()
        if int(count) >= _MAX_ATTEMPTS:
            raise RoomCodeRateLimited()
        return

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


async def record_room_code_attempt(ip: str, redis: Optional[Redis] = None) -> None:
    """Record a room code attempt for rate limiting."""
    if redis is not None:
        key = _redis_key(ip)
        now = time.time()
        member = f"{now}:{uuid.uuid4().hex[:8]}"
        pipe = redis.pipeline()
        pipe.zadd(key, {member: now})
        pipe.expire(key, _WINDOW_SECONDS + 1)
        await pipe.execute()
        return

    now = time.monotonic()
    entry_key = _key(ip)

    with _lock:
        attempts = _entries.setdefault(entry_key, deque())
        _prune(now, attempts)
        attempts.append(now)
