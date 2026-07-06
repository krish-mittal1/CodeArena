"""Leaderboard routes."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.session import get_db
from backend.services import leaderboard_service

router = APIRouter(prefix="/leaderboard", tags=["Leaderboard"])


@router.get("")
async def get_leaderboard(
    period: str = Query(default="all_time", pattern="^(all_time|weekly)$"),
    limit: int = Query(default=100, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    if period == "weekly":
        entries = await leaderboard_service.get_weekly_leaderboard(db, limit=limit)
    else:
        entries = await leaderboard_service.get_all_time_leaderboard(db, limit=limit)
    return {"period": period, "entries": entries}
