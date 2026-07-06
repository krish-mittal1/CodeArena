"""Per-user AI hint rate limiting (in-memory)."""

from __future__ import annotations

import time
from collections import defaultdict

_MAX_HINTS_PER_LEVEL_PER_DAY = 5
_WINDOW_SECONDS = 86400

_buckets: dict[str, list[float]] = defaultdict(list)


def _key(user_id: str, problem_id: str, hint_level: str) -> str:
    return f"{user_id}:{problem_id}:{hint_level}"


def ensure_hint_allowed(user_id: str, problem_id: str, hint_level: str) -> None:
    from fastapi import HTTPException, status

    now = time.time()
    k = _key(user_id, problem_id, hint_level)
    _buckets[k] = [t for t in _buckets[k] if now - t < _WINDOW_SECONDS]
    if len(_buckets[k]) >= _MAX_HINTS_PER_LEVEL_PER_DAY:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=(
                f"Daily limit for '{hint_level}' hints on this problem "
                f"({_MAX_HINTS_PER_LEVEL_PER_DAY}/day). Try again tomorrow or use a different hint level."
            ),
        )


def record_hint_use(user_id: str, problem_id: str, hint_level: str) -> None:
    """Count a hint only after it was generated successfully."""
    k = _key(user_id, problem_id, hint_level)
    _buckets[k].append(time.time())
