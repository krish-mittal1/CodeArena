"""
Matchmaking routes — join/leave queue.
Routes handle both Redis-backed and in-memory (dev-mode) matchmaking.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, status, Request
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Dict

from backend.dependencies import get_current_user, get_redis, get_db, get_client_ip
from backend.models.user import User
from backend.services import matchmaking_service, match_service
from backend.services.matchmaking_memory import memory_queue, QueueEntry
from backend.core.exceptions import AlreadyInMatch
from backend.core.room_code_rate_limit import ensure_room_code_allowed, record_room_code_attempt
from backend.core.constants import RedisKey, WSEvent
import uuid
import time
import secrets
import string

logger = logging.getLogger(__name__)

# Global memory dict for dev-mode private rooms
# Each entry: {"creator": uid, "status": "waiting"|match_id, "created_at": timestamp}
DEV_PRIVATE_ROOMS: Dict[str, dict] = {}
DEV_ROOM_TTL_SECONDS = 300  # 5 minutes, same as Redis ex=300


def _cleanup_expired_dev_rooms():
    """Remove dev-mode private rooms older than TTL."""
    now = time.time()
    expired = [code for code, room in DEV_PRIVATE_ROOMS.items()
               if now - room.get("created_at", 0) > DEV_ROOM_TTL_SECONDS]
    for code in expired:
        DEV_PRIVATE_ROOMS.pop(code, None)

router = APIRouter(prefix="/matchmaking", tags=["Matchmaking"])


@router.post("/join")
async def join_queue(
    current_user: User = Depends(get_current_user),
    redis: Optional[Redis] = Depends(get_redis),
):
    """Join the matchmaking queue."""
    if redis is not None:
        await matchmaking_service.join_queue(redis, current_user.id, current_user.elo)
        return {"status": "queued", "message": "You have been added to the matchmaking queue"}

    # Dev-mode: in-memory queue returns a dict with status
    try:
        result = await memory_queue.join_queue(current_user.id, current_user.elo)
    except Exception as exc:
        # Fail-safe: never return 500 for queue join in dev mode.
        logger.error(f"[MM-DEV] join_queue fallback triggered: {exc}", exc_info=True)
        uid = str(current_user.id)
        async with memory_queue._lock:
            if uid in memory_queue._active_matches:
                match_id = memory_queue._active_matches[uid]
                return {
                    "status": "matched",
                    "match_id": match_id,
                    "message": "You are already in an active match",
                }

            if uid not in memory_queue._pending_pair and uid not in memory_queue._queue:
                memory_queue._queue[uid] = QueueEntry(user_id=uid, elo=current_user.elo)

        return {"status": "queued", "message": "You have been added to the matchmaking queue"}

    if result["status"] == "already_matched":
        return {
            "status": "matched",
            "match_id": result["match_id"],
            "message": "You are already in an active match",
        }

    return {"status": "queued", "message": "You have been added to the matchmaking queue"}


@router.post("/join/tutorial")
async def join_tutorial_match(
    current_user: User = Depends(get_current_user),
    redis: Optional[Redis] = Depends(get_redis),
    db: AsyncSession = Depends(get_db),
):
    """Immediately start a bot match (onboarding / tutorial)."""
    from backend.services.matchmaking_service import create_immediate_bot_match
    from backend.websocket.manager import manager
    from backend.core.constants import WSEvent
    import json

    try:
        if redis is not None:
            active = await redis.get(RedisKey.user_active_match(str(current_user.id)))
            if active:
                return {"status": "matched", "match_id": active.decode() if isinstance(active, bytes) else active}
        else:
            async with memory_queue._lock:
                if str(current_user.id) in memory_queue._active_matches:
                    return {"status": "matched", "match_id": memory_queue._active_matches[str(current_user.id)]}

        match_id = await create_immediate_bot_match(db, redis, current_user.id, current_user.elo)
        match = await match_service.get_match(db, match_id)

        data = {
            "match_id": str(match_id),
            "problem_id": str(match.problem_id),
            "problem_title": match.problem.title,
            "duration_seconds": match.duration_seconds,
            "player1": {"user_id": str(match.player1_id), "username": match.player1.username, "elo": match.player1.elo},
            "player2": {"user_id": str(match.player2_id), "username": match.player2.username, "elo": match.player2.elo},
        }
        await manager.send_to_user(str(current_user.id), WSEvent.MATCH_FOUND, data)
        await manager.join_room(str(match_id), str(current_user.id))

        if redis is not None:
            await redis.publish(
                RedisKey.ws_channel(str(match_id)),
                json.dumps({"event": WSEvent.MATCH_FOUND, "data": data}),
            )

        return {"status": "matched", "match_id": str(match_id)}
    except Exception as exc:
        logger.error("Tutorial match failed: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="Could not start tutorial match") from exc


@router.delete("/leave")
async def leave_queue(
    current_user: User = Depends(get_current_user),
    redis: Optional[Redis] = Depends(get_redis),
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
    redis: Optional[Redis] = Depends(get_redis),
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
    alphabet = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


@router.post("/private/create")
async def create_private_room(
    current_user: User = Depends(get_current_user),
    redis: Optional[Redis] = Depends(get_redis),
):
    """Create a private room and return a join code."""
    uid = str(current_user.id)

    if redis is not None:
        from backend.core.constants import RedisKey
        active = await redis.get(RedisKey.user_active_match(uid))
        if active:
            raise AlreadyInMatch()

        # Remove from public queue if present
        await matchmaking_service.leave_queue(redis, current_user.id)

        # Generate unique code with collision check
        for _ in range(5):
            code = generate_room_code()
            existing = await redis.get(f"private_room:{code}")
            if not existing:
                break
        else:
            raise HTTPException(status_code=503, detail="Failed to generate unique room code, try again")

        await redis.set(f"private_room:{code}", uid, ex=300)
        await redis.set(f"private_room_status:{code}", "waiting", ex=300)
    else:
        _cleanup_expired_dev_rooms()
        if uid in memory_queue._active_matches:
            raise AlreadyInMatch()
        # Remove from public queue if present
        await memory_queue.leave_queue(current_user.id)
        for _ in range(5):
            code = generate_room_code()
            if code not in DEV_PRIVATE_ROOMS:
                break
        else:
            raise HTTPException(status_code=503, detail="Failed to generate unique room code, try again")
        DEV_PRIVATE_ROOMS[code] = {"creator": uid, "status": "waiting", "created_at": time.time()}

    return {"status": "created", "code": code}


from pydantic import BaseModel

class JoinRoomRequest(BaseModel):
    code: str

@router.post("/private/join")
async def join_private_room(
    payload: JoinRoomRequest,
    current_user: User = Depends(get_current_user),
    request: Request = None,
    redis: Optional[Redis] = Depends(get_redis),
    db: AsyncSession = Depends(get_db),
):
    """Join a private room by code."""
    # Rate limit: prevent brute force room code enumeration
    ip = get_client_ip(request) if request else "unknown"
    ensure_room_code_allowed(ip)
    record_room_code_attempt(ip)
    
    code = payload.code.upper().strip()
    if not code:
        raise HTTPException(status_code=400, detail="Room code required")

    uid_joiner = str(current_user.id)
    
    if redis is not None:
        from backend.core.constants import RedisKey
        active = await redis.get(RedisKey.user_active_match(uid_joiner))
        if active:
            raise AlreadyInMatch()

        # Atomic claim: delete the room key and check if we got it
        join_lock_key = f"lock:private_join:{code}"
        if not await redis.set(join_lock_key, uid_joiner, nx=True, ex=10):
            raise HTTPException(status_code=409, detail="Someone else is joining this room")

        try:
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
        finally:
            await redis.delete(join_lock_key)

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
    request: Request = None,
    redis: Optional[Redis] = Depends(get_redis),
):
    """Poll if a private room has been joined by an opponent."""
    code = code.upper().strip()

    # Rate limit only non-creators to prevent brute-force room code guessing.
    # The creator legitimately polls this endpoint every few seconds while waiting.
    is_creator = False
    if redis is not None:
        creator_bytes = await redis.get(f"private_room:{code}")
        if creator_bytes:
            is_creator = (creator_bytes.decode() == str(current_user.id))
    else:
        room = DEV_PRIVATE_ROOMS.get(code)
        if room:
            is_creator = (room["creator"] == str(current_user.id))

    if not is_creator:
        ip = get_client_ip(request) if request else "unknown"
        ensure_room_code_allowed(ip)
        record_room_code_attempt(ip)
        raise HTTPException(status_code=404, detail="Invalid or expired room code")

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
