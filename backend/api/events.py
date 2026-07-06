"""Live events — Saturday Cup and Weekday Blitz."""

from fastapi import APIRouter, Depends, HTTPException
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from backend.db.session import get_db
from backend.dependencies import get_redis
from backend.services import event_service

router = APIRouter(prefix="/events", tags=["Events"])


@router.get("/active")
async def list_active_events():
    events = event_service.get_active_events()
    return {"events": [event_service.event_to_dict(e) for e in events]}


@router.get("/{event_id}/leaderboard")
async def event_leaderboard(
    event_id: str,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    redis: Optional[Redis] = Depends(get_redis),
):
    active_ids = {e.id for e in event_service.get_active_events()}
    if event_id not in active_ids and not event_id.startswith("cup-"):
        # Allow fetching recent cup boards by id
        pass
    entries = await event_service.get_event_leaderboard(
        redis, db, event_id=event_id, limit=min(limit, 100)
    )
    return {"event_id": event_id, "entries": entries}
