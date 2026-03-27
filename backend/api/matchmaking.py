"""
Matchmaking routes — join/leave queue.
Routes handle both Redis-backed and in-memory (dev-mode) matchmaking.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from backend.dependencies import get_current_user, get_redis, get_db
from backend.models.user import User
from backend.services import matchmaking_service
from backend.services.matchmaking_memory import memory_queue
from backend.core.exceptions import AlreadyInMatch
import uuid
import random
import string

logger = logging.getLogger(__name__)

# Global memory dict for dev-mode private rooms
DEV_PRIVATE_ROOMS: dict[str, dict] = {}

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


def generate_room_code(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))


@router.post("/private/create")
async def create_private_room(
    current_user: User = Depends(get_current_user),
    redis: Redis | None = Depends(get_redis),
):
    """Create a private room and return a join code."""
    code = generate_room_code()
    uid = str(current_user.id)
    
    if redis is not None:
        # Check active match first
        from backend.core.constants import RedisKey
        active = await redis.get(RedisKey.user_active_match(uid))
        if active:
            raise AlreadyInMatch()
        
        await redis.set(f"private_room:{code}", uid, ex=300)
        await redis.set(f"private_room_status:{code}", "waiting", ex=300)
    else:
        # dev mode
        if uid in memory_queue._active_matches:
            raise AlreadyInMatch()
        DEV_PRIVATE_ROOMS[code] = {"creator": uid, "status": "waiting"}

    return {"status": "created", "code": code}


from pydantic import BaseModel

class JoinRoomRequest(BaseModel):
    code: str

@router.post("/private/join")
async def join_private_room(
    payload: JoinRoomRequest,
    current_user: User = Depends(get_current_user),
    redis: Redis | None = Depends(get_redis),
    db: AsyncSession = Depends(get_db),
):
    """Join a private room by code."""
    code = payload.code.upper().strip()
    if not code:
        raise HTTPException(status_code=400, detail="Room code required")

    uid_joiner = str(current_user.id)
    
    if redis is not None:
        from backend.core.constants import RedisKey
        active = await redis.get(RedisKey.user_active_match(uid_joiner))
        if active:
            raise AlreadyInMatch()

        creator_id_bytes = await redis.get(f"private_room:{code}")
        if not creator_id_bytes:
            raise HTTPException(status_code=404, detail="Invalid or expired room code")
        
        creator_id = creator_id_bytes.decode()
        if creator_id == uid_joiner:
            raise HTTPException(status_code=400, detail="Cannot join your own room")
            
        # Get creator user to get ELO
        from sqlalchemy import select
        from backend.models.user import User
        
        res = await db.execute(select(User).where(User.id == uuid.UUID(creator_id)))
        creator_user = res.scalar_one_or_none()
        if not creator_user:
            raise HTTPException(status_code=404, detail="Creator account not found")
        
        # Create match
        try:
            match_id = await matchmaking_service.create_private_match(
                db, redis,
                creator_id, creator_user.elo,
                uid_joiner, current_user.elo
            )
            # Update status for the creator to unblock their polling
            await redis.set(f"private_room_status:{code}", str(match_id), ex=300)
            await redis.delete(f"private_room:{code}")
            return {"status": "matched", "match_id": str(match_id)}
        except AlreadyInMatch:
            raise HTTPException(status_code=409, detail="One of the players is already in a match")

    else:
        # dev mode
        if uid_joiner in memory_queue._active_matches:
            raise AlreadyInMatch()
            
        room = DEV_PRIVATE_ROOMS.get(code)
        if not room:
            raise HTTPException(status_code=404, detail="Invalid or expired room code")
            
        creator_id = room["creator"]
        if creator_id == uid_joiner:
            raise HTTPException(status_code=400, detail="Cannot join your own room")
            
        from sqlalchemy import select
        from backend.models.user import User
        
        res = await db.execute(select(User).where(User.id == uuid.UUID(creator_id)))
        creator_user = res.scalar_one_or_none()
        if not creator_user:
            raise HTTPException(status_code=404, detail="Creator account not found")
        
        from backend.db.session import AsyncSessionLocal
        try:
            match_id = await memory_queue.create_private_match(
                AsyncSessionLocal,
                creator_id, creator_user.elo,
                uid_joiner, current_user.elo
            )
            room["status"] = str(match_id)
            return {"status": "matched", "match_id": str(match_id)}
        except AlreadyInMatch:
            raise HTTPException(status_code=409, detail="One of the players is already in a match")


@router.get("/private/status/{code}")
async def private_room_status(
    code: str,
    current_user: User = Depends(get_current_user),
    redis: Redis | None = Depends(get_redis),
):
    """Poll if a private room has been joined by an opponent."""
    code = code.upper().strip()
    
    if redis is not None:
        status_bytes = await redis.get(f"private_room_status:{code}")
        if not status_bytes:
            raise HTTPException(status_code=404, detail="Invalid or expired room code")
        
        status_str = status_bytes.decode()
        if status_str == "waiting":
            return {"status": "waiting"}
        return {"status": "matched", "match_id": status_str}
    else:
        room = DEV_PRIVATE_ROOMS.get(code)
        if not room:
            raise HTTPException(status_code=404, detail="Invalid or expired room code")
            
        if room["status"] == "waiting":
            return {"status": "waiting"}
        return {"status": "matched", "match_id": room["status"]}
