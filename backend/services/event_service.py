"""
Weekly events — Saturday Cup (win tracking) and weekday Blitz (bonus ELO window).

Uses Redis sorted sets when available; in-memory fallback for dev mode.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from backend.services.leaderboard_service import get_weekly_leaderboard

_memory_scores: dict[str, dict[str, float]] = {}


@dataclass
class ActiveEvent:
    id: str
    title: str
    event_type: str  # cup | blitz
    description: str
    starts_at: datetime
    ends_at: datetime
    bonus_elo_multiplier: float = 1.0


def _week_bounds(now: datetime) -> tuple[datetime, datetime]:
    """Saturday 00:00 UTC → Sunday 23:59 UTC for the current week's cup."""
    weekday = now.weekday()  # Mon=0
    days_until_saturday = (5 - weekday) % 7
    saturday = (now + timedelta(days=days_until_saturday)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    if weekday == 5 and now.hour >= 0:
        saturday = now.replace(hour=0, minute=0, second=0, microsecond=0)
    if weekday == 6:
        saturday = (now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    sunday_end = saturday + timedelta(days=1, hours=23, minutes=59, seconds=59)
    return saturday, sunday_end


def get_active_events(now: Optional[datetime] = None) -> list[ActiveEvent]:
    now = now or datetime.now(timezone.utc)
    events: list[ActiveEvent] = []

    # Saturday Cup — weekend win accumulation
    sat_start, sun_end = _week_bounds(now)
    if sat_start <= now <= sun_end:
        events.append(
            ActiveEvent(
                id=f"cup-{sat_start.strftime('%Y%m%d')}",
                title="Saturday Cup",
                event_type="cup",
                description="Win ranked battles this weekend to climb the cup leaderboard.",
                starts_at=sat_start,
                ends_at=sun_end,
            )
        )

    # Weekday Blitz — Mon–Fri 18:00–21:00 UTC, 1.5x ELO on wins
    if now.weekday() < 5:
        blitz_start = now.replace(hour=18, minute=0, second=0, microsecond=0)
        blitz_end = now.replace(hour=21, minute=0, second=0, microsecond=0)
        if blitz_start <= now <= blitz_end:
            events.append(
                ActiveEvent(
                    id=f"blitz-{now.strftime('%Y%m%d')}",
                    title="Weekday Blitz",
                    event_type="blitz",
                    description="Ranked wins during blitz hours earn 1.5× ELO.",
                    starts_at=blitz_start,
                    ends_at=blitz_end,
                    bonus_elo_multiplier=1.5,
                )
            )

    return events


def get_blitz_multiplier(now: Optional[datetime] = None) -> float:
    for event in get_active_events(now):
        if event.event_type == "blitz":
            return event.bonus_elo_multiplier
    return 1.0


def _redis_key(event_id: str) -> str:
    return f"event:scores:{event_id}"


async def record_event_win(
    redis: Optional[Redis],
    *,
    event_id: str,
    user_id: str,
    points: float = 1.0,
) -> None:
    if redis is not None:
        await redis.zincrby(_redis_key(event_id), points, user_id)
        await redis.expire(_redis_key(event_id), 60 * 60 * 24 * 14)
        return
    bucket = _memory_scores.setdefault(event_id, {})
    bucket[user_id] = bucket.get(user_id, 0.0) + points


async def get_event_leaderboard(
    redis: Optional[Redis],
    db: AsyncSession,
    *,
    event_id: str,
    limit: int = 50,
) -> list[dict]:
    if redis is not None:
        try:
            raw = await redis.zrevrange(_redis_key(event_id), 0, limit - 1, withscores=True)
            if raw:
                from sqlalchemy import select
                from backend.models.user import User

                user_ids = [uid.decode() if isinstance(uid, bytes) else uid for uid, _ in raw]
                result = await db.execute(
                    select(User.id, User.username, User.elo).where(
                        User.id.in_([__import__("uuid").UUID(uid) for uid in user_ids])
                    )
                )
                users = {str(row.id): row for row in result.all()}
                board = []
                for rank, (uid_raw, score) in enumerate(raw, start=1):
                    uid = uid_raw.decode() if isinstance(uid_raw, bytes) else str(uid_raw)
                    user = users.get(uid)
                    board.append(
                        {
                            "rank": rank,
                            "user_id": uid,
                            "username": user.username if user else "Unknown",
                            "elo": user.elo if user else 0,
                            "score": float(score),
                        }
                    )
                return board
        except Exception:
            pass

    bucket = _memory_scores.get(event_id, {})
    if bucket:
        from sqlalchemy import select
        from backend.models.user import User
        import uuid as uuid_mod

        sorted_items = sorted(bucket.items(), key=lambda x: x[1], reverse=True)[:limit]
        result = await db.execute(
            select(User.id, User.username, User.elo).where(
                User.id.in_([uuid_mod.UUID(uid) for uid, _ in sorted_items])
            )
        )
        users = {str(row.id): row for row in result.all()}
        return [
            {
                "rank": idx + 1,
                "user_id": uid,
                "username": users[uid].username if uid in users else "Unknown",
                "elo": users[uid].elo if uid in users else 0,
                "score": score,
            }
            for idx, (uid, score) in enumerate(sorted_items)
        ]

    # Fallback: weekly wins from DB
    weekly = await get_weekly_leaderboard(db, limit=limit)
    return [
        {**row, "score": float(row.get("weekly_wins", 0))}
        for row in weekly
    ]


def event_to_dict(event: ActiveEvent) -> dict:
    now = datetime.now(timezone.utc)
    return {
        "id": event.id,
        "title": event.title,
        "type": event.event_type,
        "description": event.description,
        "starts_at": event.starts_at.isoformat(),
        "ends_at": event.ends_at.isoformat(),
        "seconds_remaining": max(0, int((event.ends_at - now).total_seconds())),
        "bonus_elo_multiplier": event.bonus_elo_multiplier,
    }
