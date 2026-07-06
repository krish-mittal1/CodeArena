"""Spaced review queue and practice streaks."""

from __future__ import annotations

import hashlib
import uuid
from datetime import date, datetime, timedelta, timezone

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.problem import Problem
from backend.models.review_queue import ReviewQueueItem
from backend.models.user import User

REVIEW_INTERVALS = [3, 7, 21]


async def schedule_review_after_solve(db: AsyncSession, user_id: uuid.UUID, problem_id: uuid.UUID) -> None:
    """Schedule first review in 3 days when user solves a problem."""
    existing = await db.execute(
        select(ReviewQueueItem).where(
            ReviewQueueItem.user_id == user_id,
            ReviewQueueItem.problem_id == problem_id,
            ReviewQueueItem.completed_at.is_(None),
        )
    )
    if existing.scalar_one_or_none():
        return

    due = datetime.now(timezone.utc) + timedelta(days=REVIEW_INTERVALS[0])
    db.add(ReviewQueueItem(
        user_id=user_id,
        problem_id=problem_id,
        due_at=due,
        interval_days=REVIEW_INTERVALS[0],
    ))


async def get_due_reviews(db: AsyncSession, user_id: uuid.UUID, limit: int = 10) -> list[dict]:
    now = datetime.now(timezone.utc)
    result = await db.execute(
        select(ReviewQueueItem, Problem)
        .join(Problem, Problem.id == ReviewQueueItem.problem_id)
        .where(
            ReviewQueueItem.user_id == user_id,
            ReviewQueueItem.due_at <= now,
            ReviewQueueItem.completed_at.is_(None),
        )
        .order_by(ReviewQueueItem.due_at)
        .limit(limit)
    )
    items = []
    for row, problem in result.all():
        items.append({
            "id": str(row.id),
            "problem_id": str(problem.id),
            "problem_title": problem.title,
            "difficulty": problem.difficulty,
            "due_at": row.due_at.isoformat(),
            "interval_days": row.interval_days,
        })
    return items


async def complete_review(db: AsyncSession, user_id: uuid.UUID, review_id: uuid.UUID) -> None:
    result = await db.execute(
        select(ReviewQueueItem).where(
            ReviewQueueItem.id == review_id,
            ReviewQueueItem.user_id == user_id,
        )
    )
    item = result.scalar_one_or_none()
    if not item:
        return
    item.completed_at = datetime.now(timezone.utc)


async def bump_practice_streak(db: AsyncSession, user: User) -> int:
    today = date.today()
    if user.last_practice_date == today:
        return user.practice_streak
    if user.last_practice_date == today - timedelta(days=1):
        user.practice_streak += 1
    else:
        user.practice_streak = 1
    user.last_practice_date = today
    await db.flush()
    return user.practice_streak


def pick_daily_problem_id(problems: list[Problem], day: date | None = None) -> uuid.UUID | None:
    if not problems:
        return None
    day = day or date.today()
    seed = day.isoformat().encode()
    idx = int(hashlib.md5(seed).hexdigest(), 16) % len(problems)
    dsa = [p for p in problems if p.problem_type == "dsa"]
    if not dsa:
        return problems[0].id
    idx = int(hashlib.md5(seed).hexdigest(), 16) % len(dsa)
    return dsa[idx].id
