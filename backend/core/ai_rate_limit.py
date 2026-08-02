"""Per-user AI rate limiting for hints and code analysis (Redis with in-memory fallback)."""

from __future__ import annotations

import time
import uuid
from collections import defaultdict
from threading import Lock
from typing import Optional

from redis.asyncio import Redis

# ── Hint rate limits ──────────────────────────────────────────────────────────
_MAX_HINTS_PER_LEVEL_PER_DAY = 5
_HINT_WINDOW_SECONDS = 86400

_hint_buckets: dict[str, list[float]] = defaultdict(list)


def _hint_key(user_id: str, problem_id: str, hint_level: str) -> str:
    return f"{user_id}:{problem_id}:{hint_level}"


def _hint_redis_key(user_id: str, problem_id: str, hint_level: str) -> str:
    return f"ratelimit:hint:{user_id}:{problem_id}:{hint_level}"


async def ensure_hint_allowed(
    user_id: str,
    problem_id: str,
    hint_level: str,
    redis: Optional[Redis] = None,
) -> None:
    from fastapi import HTTPException, status

    if redis is not None:
        key = _hint_redis_key(user_id, problem_id, hint_level)
        now = time.time()
        pipe = redis.pipeline()
        pipe.zremrangebyscore(key, 0, now - _HINT_WINDOW_SECONDS)
        pipe.zcard(key)
        _, count = await pipe.execute()
        if int(count) >= _MAX_HINTS_PER_LEVEL_PER_DAY:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=(
                    f"Daily limit for '{hint_level}' hints on this problem "
                    f"({_MAX_HINTS_PER_LEVEL_PER_DAY}/day). Try again tomorrow or use a different hint level."
                ),
            )
        return

    now = time.time()
    k = _hint_key(user_id, problem_id, hint_level)
    _hint_buckets[k] = [t for t in _hint_buckets[k] if now - t < _HINT_WINDOW_SECONDS]
    if len(_hint_buckets[k]) >= _MAX_HINTS_PER_LEVEL_PER_DAY:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=(
                f"Daily limit for '{hint_level}' hints on this problem "
                f"({_MAX_HINTS_PER_LEVEL_PER_DAY}/day). Try again tomorrow or use a different hint level."
            ),
        )


async def record_hint_use(
    user_id: str,
    problem_id: str,
    hint_level: str,
    redis: Optional[Redis] = None,
) -> None:
    """Count a hint only after it was generated successfully."""
    if redis is not None:
        key = _hint_redis_key(user_id, problem_id, hint_level)
        now = time.time()
        member = f"{now}:{uuid.uuid4().hex[:8]}"
        pipe = redis.pipeline()
        pipe.zadd(key, {member: now})
        pipe.expire(key, _HINT_WINDOW_SECONDS + 1)
        await pipe.execute()
        return

    k = _hint_key(user_id, problem_id, hint_level)
    _hint_buckets[k].append(time.time())


# ── AI Analysis rate limits ───────────────────────────────────────────────────
# Max 10 analysis calls per user per hour.
#
# Quota counts only real successful LLM responses (see AnalyzeCodeResult.used_llm),
# not cache hits and not fallback/error placeholders.
#
# TOCTOU: acquire_analysis_slot atomically reserves a slot (Lua ZADD-if-under-max
# / in-memory lock). Callers must release_analysis_slot when the LLM was not used.
# record_analysis_use is a no-op confirm kept for readable call sites.

_MAX_ANALYSIS_PER_HOUR = 10
_ANALYSIS_WINDOW_SECONDS = 3600

_analysis_buckets: dict[str, list[tuple[float, str]]] = defaultdict(list)
_analysis_lock = Lock()

# KEYS[1]=key  ARGV[1]=now ARGV[2]=window ARGV[3]=max ARGV[4]=member
_ANALYSIS_RESERVE_LUA = """
redis.call('ZREMRANGEBYSCORE', KEYS[1], 0, tonumber(ARGV[1]) - tonumber(ARGV[2]))
local count = redis.call('ZCARD', KEYS[1])
if count >= tonumber(ARGV[3]) then
  return 0
end
redis.call('ZADD', KEYS[1], tonumber(ARGV[1]), ARGV[4])
redis.call('EXPIRE', KEYS[1], tonumber(ARGV[2]) + 1)
return 1
"""


def _analysis_redis_key(user_id: str) -> str:
    return f"ratelimit:ai_analysis:{user_id}"


def _analysis_429():
    from fastapi import HTTPException, status

    return HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail=(
            f"Analysis limit reached ({_MAX_ANALYSIS_PER_HOUR}/hour). "
            "Try again later — cached results for the same submission are instant."
        ),
    )


async def acquire_analysis_slot(
    user_id: str,
    redis: Optional[Redis] = None,
) -> str:
    """
    Atomically reserve one analysis quota slot. Returns a reservation token.
    Raise HTTP 429 if the hourly limit is already reached.
    Caller must release_analysis_slot(token) if the LLM was not actually used.
    """
    member = f"{time.time()}:{uuid.uuid4().hex[:12]}"

    if redis is not None:
        key = _analysis_redis_key(user_id)
        now = time.time()
        ok = await redis.eval(
            _ANALYSIS_RESERVE_LUA,
            1,
            key,
            str(now),
            str(_ANALYSIS_WINDOW_SECONDS),
            str(_MAX_ANALYSIS_PER_HOUR),
            member,
        )
        if int(ok) != 1:
            raise _analysis_429()
        return member

    now = time.time()
    with _analysis_lock:
        bucket = [
            (t, m)
            for t, m in _analysis_buckets[user_id]
            if now - t < _ANALYSIS_WINDOW_SECONDS
        ]
        if len(bucket) >= _MAX_ANALYSIS_PER_HOUR:
            _analysis_buckets[user_id] = bucket
            raise _analysis_429()
        bucket.append((now, member))
        _analysis_buckets[user_id] = bucket
    return member


async def release_analysis_slot(
    user_id: str,
    reservation: str,
    redis: Optional[Redis] = None,
) -> None:
    """Release a previously acquired slot (cache hit / fallback / error)."""
    if redis is not None:
        await redis.zrem(_analysis_redis_key(user_id), reservation)
        return

    with _analysis_lock:
        _analysis_buckets[user_id] = [
            (t, m) for t, m in _analysis_buckets[user_id] if m != reservation
        ]


async def ensure_analysis_allowed(
    user_id: str,
    redis: Optional[Redis] = None,
) -> str:
    """
    Reserve an analysis quota slot (atomic). Returns reservation token.
    Prefer acquire_analysis_slot; this alias preserves older call-site names.
    """
    return await acquire_analysis_slot(user_id, redis=redis)


async def record_analysis_use(
    user_id: str,
    redis: Optional[Redis] = None,
    reservation: Optional[str] = None,
) -> None:
    """
    Confirm a successful LLM analysis against the user's hourly quota.

    When ensure_analysis_allowed/acquire_analysis_slot already reserved a slot,
    this is a no-op (the reservation stays counted). Kept so call sites read
    clearly: acquire → analyze → record on used_llm / release otherwise.
    """
    return None
