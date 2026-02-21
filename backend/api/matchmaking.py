"""
Matchmaking routes — join/leave queue.
Routes handle both Redis-backed and in-memory (dev-mode) matchmaking.
"""

import logging

from fastapi import APIRouter, Depends
from redis.asyncio import Redis

from backend.dependencies import get_current_user, get_redis
from backend.models.user import User
from backend.services import matchmaking_service
from backend.services.matchmaking_memory import memory_queue

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/matchmaking", tags=["Matchmaking"])


@router.post("/join")
async def join_queue(
    current_user: User = Depends(get_current_user),
    redis: Redis | None = Depends(get_redis),
):
    """Join the matchmaking queue."""
    if redis is not None:
        await matchmaking_service.join_queue(redis, current_user.id, current_user.elo)
        return {"status": "queued", "message": "You have been added to the matchmaking queue"}

    # Dev-mode: in-memory queue returns a dict with status
    result = await memory_queue.join_queue(current_user.id, current_user.elo)

    if result["status"] == "already_matched":
        return {
            "status": "matched",
            "match_id": result["match_id"],
            "message": "You are already in an active match",
        }

    return {"status": "queued", "message": "You have been added to the matchmaking queue"}


@router.delete("/leave")
async def leave_queue(
    current_user: User = Depends(get_current_user),
    redis: Redis | None = Depends(get_redis),
):
    """Leave the matchmaking queue."""
    if redis is not None:
        await matchmaking_service.leave_queue(redis, current_user.id)
    else:
        await memory_queue.leave_queue(current_user.id)

    return {"status": "removed", "message": "You have been removed from the matchmaking queue"}


@router.get("/status")
async def queue_status(
    current_user: User = Depends(get_current_user),
    redis: Redis | None = Depends(get_redis),
):
    """Check queue position, wait time, and current ELO window."""
    if redis is not None:
        info = await matchmaking_service.get_queue_position(redis, current_user.id)
    else:
        info = await memory_queue.get_queue_position(current_user.id)

    if not info:
        return {"status": "not_in_queue"}
    return {"status": "queued", **info}
