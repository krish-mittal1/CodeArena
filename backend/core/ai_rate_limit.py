"""Per-user AI hint rate limiting (in-memory)."""

from __future__ import annotations

import time
from collections import defaultdict

_MAX_HINTS_PER_PROBLEM_PER_DAY = 3
_WINDOW_SECONDS = 86400

_buckets: dict[str, list[float]] = defaultdict(list)


def _key(user_id: str, problem_id: str) -> str:
    return f"{user_id}:{problem_id}"


def ensure_hint_allowed(user_id: str, problem_id: str) -> None:
    from fastapi import HTTPException, status

    now = time.time()
    k = _key(user_id, problem_id)
    _buckets[k] = [t for t in _buckets[k] if now - t < _WINDOW_SECONDS]
    if len(_buckets[k]) >= _MAX_HINTS_PER_PROBLEM_PER_DAY:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Hint limit reached ({_MAX_HINTS_PER_PROBLEM_PER_DAY} per problem per day).",
        )
    _buckets[k].append(now)
