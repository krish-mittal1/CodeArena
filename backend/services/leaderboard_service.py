"""Leaderboard queries — all-time ELO and weekly activity."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.match import Match
from backend.models.user import User
from backend.core.constants import MatchStatus


async def get_all_time_leaderboard(db: AsyncSession, *, limit: int = 100) -> list[dict]:
    result = await db.execute(
        select(User.id, User.username, User.elo, User.matches_won, User.matches_played)
        .where(User.is_bot.is_(False))
        .order_by(User.elo.desc(), User.matches_won.desc())
        .limit(limit)
    )
    rows = result.all()
    return [
        {
            "rank": idx + 1,
            "user_id": str(row.id),
            "username": row.username,
            "elo": row.elo,
            "matches_won": row.matches_won,
            "matches_played": row.matches_played,
        }
        for idx, row in enumerate(rows)
    ]


async def get_weekly_leaderboard(db: AsyncSession, *, limit: int = 100) -> list[dict]:
    """Rank by wins in the last 7 days (non-bot users)."""
    week_ago = datetime.now(timezone.utc) - timedelta(days=7)

    wins_subq = (
        select(
            Match.winner_id.label("user_id"),
            func.count().label("weekly_wins"),
        )
        .where(
            Match.status == MatchStatus.COMPLETED,
            Match.ended_at.is_not(None),
            Match.ended_at >= week_ago,
            Match.winner_id.is_not(None),
        )
        .group_by(Match.winner_id)
        .subquery()
    )

    result = await db.execute(
        select(
            User.id,
            User.username,
            User.elo,
            func.coalesce(wins_subq.c.weekly_wins, 0).label("weekly_wins"),
        )
        .outerjoin(wins_subq, User.id == wins_subq.c.user_id)
        .where(User.is_bot.is_(False))
        .order_by(func.coalesce(wins_subq.c.weekly_wins, 0).desc(), User.elo.desc())
        .limit(limit)
    )

    rows = result.all()
    return [
        {
            "rank": idx + 1,
            "user_id": str(row.id),
            "username": row.username,
            "elo": row.elo,
            "weekly_wins": int(row.weekly_wins or 0),
        }
        for idx, row in enumerate(rows)
    ]
