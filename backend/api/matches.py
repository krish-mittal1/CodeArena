"""
Match routes — match details and history.
"""

import uuid
import json

from fastapi import APIRouter, Depends, Query
from typing import Optional, List
from redis.asyncio import Redis

from backend.db.session import get_db, AsyncSession
from backend.dependencies import get_current_user, get_redis
from backend.models.user import User
from backend.schemas.match import MatchResponse, MatchHistoryItem
from backend.services import match_service
from backend.core.constants import RedisKey, WSEvent
from backend.websocket.manager import manager

router = APIRouter(prefix="/matches", tags=["Matches"])


@router.get("/{match_id}", response_model=MatchResponse)
async def get_match(
    match_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get match details by ID."""
    return await match_service.get_match(db, match_id)


@router.get("/history/me", response_model=List[MatchHistoryItem])
async def get_match_history(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get match history for the current user."""
    matches = await match_service.get_match_history(db, current_user.id, limit, offset)
    user_id = current_user.id

    history = []
    for m in matches:
        is_player1 = m.player1_id == user_id
        opponent = m.player2 if is_player1 else m.player1
        elo_before = m.player1_elo_before if is_player1 else m.player2_elo_before
        elo_after = m.player1_elo_after if is_player1 else m.player2_elo_after

        if m.winner_id is None:
            result = "draw"
        elif m.winner_id == user_id:
            result = "win"
        else:
            result = "loss"

        history.append(MatchHistoryItem(
            id=m.id,
            opponent_username=opponent.username,
            opponent_elo=opponent.elo,
            your_elo_before=elo_before,
            your_elo_after=elo_after,
            result=result,
            started_at=m.started_at,
            duration_seconds=m.duration_seconds,
        ))

    return history


@router.post("/{match_id}/forfeit")
async def forfeit_match(
    match_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    redis: Optional[Redis] = Depends(get_redis),
):
    """
    Forfeit an active match.

    Behavior:
      - Only participants can forfeit
      - If match already completed → no-op (idempotent)
      - Opponent is declared winner and ELO updated
      - WebSocket match_ended is sent to both players (and spectators)
    """
    result = await match_service.forfeit_match(db, redis, match_id, current_user.id)

    # Already completed / non-active → treat as success, nothing to broadcast
    if not result:
        return {"status": "already_completed"}

    room_id = str(match_id)

    # Redis-backed mode: publish event for all pods
    if redis is not None:
        channel = RedisKey.ws_channel(room_id)
        await redis.publish(
            channel,
            json.dumps({
                "event": WSEvent.MATCH_ENDED,
                "data": result,
            }),
        )
    else:
        # Dev-mode (no Redis): broadcast directly via ConnectionManager
        await manager.broadcast_match_ended(room_id, result)

    # Dev-mode matchmaking uses in-memory active_matches tracking; clear it safely
    if redis is None:
        try:
            from backend.services.matchmaking_memory import memory_queue

            memory_queue.clear_match_for_both(result["player1_id"], result["player2_id"])
        except Exception:
            # Best-effort cleanup — stale mappings are tolerated
            pass

    return {"status": "forfeited"}
