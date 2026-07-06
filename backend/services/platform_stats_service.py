"""Live platform stats for dashboard (queue depth, online users, wait estimate)."""

from __future__ import annotations

import time
from typing import Optional

from redis.asyncio import Redis

from backend.config import settings
from backend.core.constants import RedisKey
from backend.services.matchmaking_memory import memory_queue
from backend.services.matchmaking_service import _parse_queue_entries
from backend.websocket.manager import manager


async def get_platform_stats(redis: Optional[Redis]) -> dict:
    """Return queue size, connected users, active battles, and estimated wait."""
    online_users = await manager.get_connected_user_count()
    active_rooms = await manager.get_active_rooms()
    active_battles = len(active_rooms)

    queue_size = 0
    oldest_wait_secs = 0.0

    if redis is not None:
        try:
            queue_entries = await redis.zrangebyscore(
                RedisKey.MATCHMAKING_QUEUE, "-inf", "+inf", withscores=True
            )
            queue_size = len(queue_entries)
            if queue_entries:
                players = _parse_queue_entries(queue_entries)
                if players:
                    oldest_wait_secs = max(0.0, time.time() - min(p["joined_at"] for p in players))
        except Exception:
            queue_size = 0
    else:
        async with memory_queue._lock:
            queue_size = len(memory_queue._queue)
            if memory_queue._queue:
                oldest_wait_secs = max(
                    0.0,
                    time.time() - min(e.joined_at for e in memory_queue._queue.values()),
                )

    # Rough wait estimate: pairing needs 2 players or bot fallback timer
    if queue_size <= 1:
        remaining = max(0, settings.matchmaking_bot_fallback_seconds - int(oldest_wait_secs))
        estimated_wait_seconds = remaining if queue_size == 1 else 0
    else:
        estimated_wait_seconds = max(3, min(30, int(oldest_wait_secs / 2)))

    return {
        "online_users": online_users,
        "queue_size": queue_size,
        "active_battles": active_battles,
        "estimated_wait_seconds": estimated_wait_seconds,
    }
