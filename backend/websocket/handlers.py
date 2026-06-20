"""
WebSocket event handlers — player connection lifecycle, spectator handling,
and incoming message routing.

Design:
  - Players authenticate via JWT token in query param
  - One active WS connection per user (old one is replaced)
  - Players auto-join their match room when the server detects an active match
  - Spectators connect to a specific match room in read-only mode
  - All game actions go through REST (not WS) — WS is push-only for events
"""

import json
import logging
import asyncio
import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import WebSocket, WebSocketDisconnect
from redis.asyncio import Redis

from backend.config import settings
from backend.core.constants import WSEvent, RedisKey
from backend.core.security import decode_token
from backend.websocket.manager import manager
from backend.services import matchmaking_service
from backend.services.matchmaking_memory import memory_queue
from backend.db.session import AsyncSessionLocal
from backend.core.constants import MatchStatus
from backend.models.match import Match
from sqlalchemy import select
from sqlalchemy.orm import selectinload

logger = logging.getLogger(__name__)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Player WebSocket Handler
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def handle_player_connection(websocket: WebSocket, token: str, redis: Optional[Redis]):
    """
    Full lifecycle of a player's WebSocket connection:

      1. Validate JWT → extract user_id
      2. Register connection in ConnectionManager
      3. Auto-join active match room (if any) — handles reconnection
      4. Enter receive loop (heartbeats only — game actions use REST)
      5. On disconnect → clean up rooms + notify opponent

    Args:
        websocket: The FastAPI WebSocket object
        token: JWT access token from query param (?token=...)
        redis: Redis connection for checking active match
    """
    # ── 1. Authenticate ───────────────────────────────────
    try:
        payload = decode_token(token)
        user_id = payload["sub"]
        username = payload.get("username", "unknown")
    except Exception:
        await websocket.close(code=4001, reason="Invalid or expired token")
        return

    # ── 2. Register connection ────────────────────────────
    await manager.connect_player(user_id, websocket)

    try:
        # ── 3. Auto-join active match room ────────────────
        await _auto_join_match_room(user_id, redis)
        # Recovery: if Redis is disabled/unavailable OR if Redis auto-join didn't find
        # a match room, fall back to DB recovery. This handles cases where match_found
        # was missed due to reconnect timing or stale Redis state.
        if not await manager.is_user_in_any_room(user_id):
            await _recover_active_match_from_db(user_id, redis=redis)

        # ── 4. Send connection acknowledgment ─────────────
        await manager.send_to_user(user_id, "connected", {
            "user_id": user_id,
            "username": username,
            "message": "WebSocket connection established",
        })

        # ── 5. Receive loop ──────────────────────────────
        await _player_receive_loop(user_id, websocket, redis)

    except WebSocketDisconnect:
        logger.info(f"[WS] Player {user_id} disconnected (clean)")
    except Exception as e:
        logger.error(f"[WS] Player {user_id} error: {e}", exc_info=True)
    finally:
        # Always remove player from matchmaking queue on disconnect to prevent stale entries.
        # This is safe because leave_queue is idempotent in both Redis and dev-memory modes.
        try:
            if redis is not None:
                await matchmaking_service.leave_queue(redis, uuid.UUID(user_id))
            else:
                await memory_queue.leave_queue(uuid.UUID(user_id))
        except Exception as e:
            logger.debug(f"[WS] Failed to auto-leave matchmaking for {user_id}: {e}", exc_info=True)

        # ── 6. Cleanup ────────────────────────────────────
        await manager.disconnect_player(user_id)


async def _auto_join_match_room(user_id: str, redis: Optional[Redis]):
    """
    Check if the user has an active match in Redis.
    If so, auto-join the room — handles reconnection gracefully.
    
    PRODUCTION: Handles Redis failures and stale data gracefully.
    """
    if redis is None:
        return
    
    try:
        active_match = await asyncio.wait_for(
            redis.get(RedisKey.user_active_match(user_id)),
            timeout=2
        )
        if active_match:
            match_id = active_match.decode() if isinstance(active_match, bytes) else active_match
            
            # Verify match still exists and is active
            match_state = await redis.hgetall(RedisKey.match_state(match_id))
            if match_state:
                await _recover_active_match_from_db(user_id, expected_match_id=match_id, redis=redis)
            else:
                # Match expired, clean up stale active_match key
                await redis.delete(RedisKey.user_active_match(user_id))
                logger.debug(f"[WS] Player {user_id} had stale active_match, cleaned up")
    except asyncio.TimeoutError:
        logger.warning(f"[WS] Redis timeout checking active match for {user_id}")
    except Exception as e:
        logger.error(f"[WS] Error auto-joining match room for {user_id}: {e}")


async def _recover_active_match_from_db(
    user_id: str,
    expected_match_id: Optional[str] = None,
    redis: Optional[Redis] = None,
) -> None:
    """
    Recovery mechanism (no-Redis mode):
      - If user has an ACTIVE match in Postgres, (re)send match_found,
        join them to the room, and sync remaining time.
      - Safe to call on every WS connect.
    """
    try:
        uid = uuid.UUID(user_id)
    except Exception:
        return

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Match)
            .where(
                (Match.status == MatchStatus.ACTIVE)
                & ((Match.player1_id == uid) | (Match.player2_id == uid))
                & (Match.id == uuid.UUID(expected_match_id) if expected_match_id else True)
            )
            .order_by(Match.started_at.desc())
            .options(
                selectinload(Match.player1),
                selectinload(Match.player2),
                selectinload(Match.problem),
            )
            .limit(1)
        )
        match = result.scalar_one_or_none()

    if not match:
        return

    room_id = str(match.id)
    already_joined = await manager.is_user_in_room(room_id, user_id)
    if not already_joined:
        await manager.join_room(room_id, user_id)

    # Rebuild match_found payload (must match frontend expectations)
    payload = {
        "match_id": room_id,
        "problem_id": str(match.problem_id),
        "problem_title": match.problem.title if match.problem else "",
        "player1": {
            "user_id": str(match.player1.id),
            "username": match.player1.username,
            "elo": match.player1.elo,
        },
        "player2": {
            "user_id": str(match.player2.id),
            "username": match.player2.username,
            "elo": match.player2.elo,
        },
        "duration_seconds": match.duration_seconds,
    }

    await manager.send_to_user(user_id, WSEvent.MATCH_FOUND, payload)

    # Timer sync based on Redis timer in prod, DB started_at otherwise
    remaining = await _get_remaining_time(redis, room_id) if redis is not None else None
    if remaining is None:
        try:
            started_at = match.started_at
            if started_at.tzinfo is None:
                started_at = started_at.replace(tzinfo=timezone.utc)
            elapsed = (datetime.now(timezone.utc) - started_at).total_seconds()
            remaining = max(0, int(match.duration_seconds - elapsed))
        except Exception:
            remaining = match.duration_seconds

    await manager.send_to_user(user_id, WSEvent.MATCH_TIMER_SYNC, {"remaining_seconds": remaining})
    await manager.send_to_user(user_id, "room_joined", {
        "match_id": room_id,
        "remaining_seconds": remaining,
        "reconnected": True,
    })

    logger.info(f"[WS] Recovered active match for {user_id} → {room_id} (remaining={remaining}s)")


async def _player_receive_loop(user_id: str, websocket: WebSocket, redis: Optional[Redis]):
    """
    Listen for incoming messages from the player.
    Only heartbeats are expected — game actions use REST endpoints.
    """
    while True:
        raw = await websocket.receive_text()

        try:
            message = json.loads(raw)
        except json.JSONDecodeError:
            await manager.send_to_user(user_id, WSEvent.ERROR, {
                "code": "INVALID_JSON",
                "message": "Message must be valid JSON with {event, data}",
            })
            continue

        event = message.get("event")
        data = message.get("data", {})

        # ── Route events ──────────────────────────────────
        if event == WSEvent.HEARTBEAT:
            # Keep-alive — respond with pong for latency measurement
            await manager.send_to_user(user_id, "pong", {})

        elif event == "ping":
            # Alternative keep-alive format
            await manager.send_to_user(user_id, "pong", {})

        elif event == "get_room_info":
            # Client requesting room metadata
            match_id = data.get("match_id")
            if match_id:
                info = await manager.get_room_info(match_id)
                await manager.send_to_user(user_id, "room_info", info or {"error": "not_found"})

        else:
            logger.debug(f"[WS] Unknown event from {user_id}: {event}")
            await manager.send_to_user(user_id, WSEvent.ERROR, {
                "code": "UNKNOWN_EVENT",
                "message": f"Unknown event: {event}. Game actions should use REST endpoints.",
            })


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Spectator WebSocket Handler
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def handle_spectator_connection(
    websocket: WebSocket,
    match_id: str,
    redis: Optional[Redis],
    token: Optional[str] = None,
):
    """
    Handle a spectator's read-only WebSocket connection.

      1. Validate authentication (if required by config)
      2. Validate the match exists and is active
      3. Join the room as a spectator
      4. Send initial room state (players, remaining time)
      5. Receive loop (heartbeats only, reject anything else)
      6. Clean up on disconnect

    Args:
        websocket: The FastAPI WebSocket object
        match_id: Match UUID from the URL path
        redis: Redis connection for match state lookup
        token: Optional JWT token for spectator auth
        
    SECURITY: Spectator authentication is enforced by default (config: spectator_require_auth=True)
    """
    from backend.config import settings
    
    # ✓ FIXED: Enforce spectator authentication by default
    if settings.spectator_require_auth:
        if not token:
            await websocket.close(code=4001, reason="Authentication required")
            return
        try:
            decode_token(token)
        except Exception:
            await websocket.close(code=4001, reason="Invalid or expired token")
            return

    # ── 1. Validate match exists ──────────────────────────
    if redis is None:
        await websocket.close(code=4003, reason="Spectating unavailable (Redis disabled)")
        return
    match_state = await redis.hgetall(RedisKey.match_state(match_id))
    if not match_state:
        await websocket.close(code=4004, reason="Match not found or already ended")
        return

    # ── 2. Join room as spectator ─────────────────────────
    room_info = await manager.add_spectator(match_id, websocket)

    try:
        # ── 3. Send initial state ─────────────────────────
        p1_id = match_state.get(b"player1_id", b"").decode()
        p2_id = match_state.get(b"player2_id", b"").decode()
        problem_title = match_state.get(b"problem_title", b"").decode()
        remaining = await _get_remaining_time(redis, match_id)

        await websocket.send_json({
            "event": WSEvent.SPECTATOR_JOINED,
            "data": {
                "match_id": match_id,
                "player1_id": p1_id,
                "player2_id": p2_id,
                "problem_title": problem_title,
                "remaining_seconds": remaining,
                "spectator_count": room_info.get("spectator_count", 0) if room_info else 0,
            },
        })

        # ── 4. Receive loop (read-only) ──────────────────
        while True:
            raw = await websocket.receive_text()
            try:
                message = json.loads(raw)
                event = message.get("event")

                if event in (WSEvent.HEARTBEAT, "ping"):
                    await websocket.send_json({"event": "pong", "data": {}})
                else:
                    await websocket.send_json({
                        "event": WSEvent.ERROR,
                        "data": {
                            "code": "READ_ONLY",
                            "message": "Spectators cannot send events",
                        },
                    })
            except json.JSONDecodeError:
                pass

    except WebSocketDisconnect:
        logger.info(f"[WS] Spectator left room {match_id}")
    except Exception as e:
        logger.error(f"[WS] Spectator error in room {match_id}: {e}")
    finally:
        await manager.remove_spectator(match_id, websocket)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Helpers
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def _get_remaining_time(redis: Optional[Redis], match_id: str) -> Optional[int]:
    """Read match expiry timestamp from Redis and compute remaining seconds."""
    if redis is None:
        return None
    timer_val = await redis.get(RedisKey.match_timer(match_id))
    if not timer_val:
        return None
    import time
    expiry = float(timer_val)
    return max(0, int(expiry - time.time()))
