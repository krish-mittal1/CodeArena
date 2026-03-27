from typing import Optional, Union
"""
WebSocket ConnectionManager — production-grade, async-safe, room-based
event broadcasting with Redis pub/sub for horizontal scaling.

Architecture (dual-layer):
  ┌──────────────────────────────────────────────────────┐
  │  Pod A                     Pod B                     │
  │  ┌──────────────┐          ┌──────────────┐         │
  │  │ Local rooms   │          │ Local rooms   │         │
  │  │ dict[room_id, │          │ dict[room_id, │         │
  │  │   set[WS]]    │          │   set[WS]]    │         │
  │  └──────┬───────┘          └──────┬───────┘         │
  │         │ PUBLISH                  │ SUBSCRIBE       │
  │         └──────── Redis ──────────┘                  │
  └──────────────────────────────────────────────────────┘

Every broadcast:
  1. Sends to local connections (fast, no network hop)
  2. PUBLISHes to Redis channel (other pods pick it up)
  3. Other pods' SUB listener calls _dispatch_local (no echo)

Thread safety:
  All mutable state is protected by asyncio.Lock to prevent
  corruption from concurrent coroutines (e.g., two users
  connecting/disconnecting simultaneously).
"""

import json
import logging
import asyncio
from dataclasses import dataclass, field

from fastapi import WebSocket
from redis.asyncio import Redis

from backend.core.constants import RedisKey, WSEvent

logger = logging.getLogger(__name__)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Room metadata (for introspection / admin endpoints)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@dataclass
class BattleRoom:
    """Represents one match room with players + spectators."""
    room_id: str
    players: dict[str, WebSocket] = field(default_factory=dict)      # user_id → ws
    spectators: set[WebSocket] = field(default_factory=set)

    @property
    def player_count(self) -> int:
        return len(self.players)

    @property
    def spectator_count(self) -> int:
        return len(self.spectators)

    @property
    def total_connections(self) -> int:
        return self.player_count + self.spectator_count

    @property
    def is_empty(self) -> bool:
        return self.total_connections == 0

    @property
    def all_websockets(self) -> list[WebSocket]:
        """All connections (players + spectators) for broadcasting."""
        return list(self.players.values()) + list(self.spectators)

    def info(self) -> dict:
        return {
            "room_id": self.room_id,
            "players": list(self.players.keys()),
            "player_count": self.player_count,
            "spectator_count": self.spectator_count,
        }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  ConnectionManager
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class ConnectionManager:
    """
    Manages WebSocket connections organized into BattleRooms.

    Async safety:
      - _lock protects all mutable state (_rooms, _user_ws, _user_rooms)
      - Every public method acquires the lock before touching state
      - Actual I/O (ws.send_json) is done OUTSIDE the lock where possible
        to avoid holding the lock during slow network calls

    Cross-instance:
      - Redis Pub/Sub — every broadcast publishes to a Redis channel
      - A dedicated listener task receives messages from Redis and dispatches
        to local connections, with a source_instance_id guard to avoid echo
    """

    def __init__(self):
        # ── State (protected by _lock) ────────────────────
        self._rooms: dict[str, BattleRoom] = {}
        self._user_ws: dict[str, WebSocket] = {}         # user_id → ws
        self._user_rooms: dict[str, set[str]] = {}        # user_id → set of room_ids

        # ── Async safety ──────────────────────────────────
        self._lock = asyncio.Lock()

        # ── Redis pub/sub ─────────────────────────────────
        self._redis: Optional[Redis] = None
        self._pubsub = None
        self._listener_task: asyncio.Task | None = None
        self._instance_id = id(self)  # Unique per process (echo guard)

    # ── Lifecycle ─────────────────────────────────────────────

    async def init(self, redis: Optional[Redis]):
        """
        Initialize Redis pub/sub listener. Called once at app startup.
        
        PRODUCTION: Ensures initialization completes within timeout.
        """
        if redis is None:
            logger.info("[WS] ConnectionManager initialized WITHOUT Redis (local-only mode)")
            return
        
        try:
            # Test Redis connection
            await asyncio.wait_for(redis.ping(), timeout=2)
            self._redis = redis
            self._pubsub = redis.pubsub()
            self._listener_task = asyncio.create_task(
                self._redis_listener(), name="ws-pubsub-listener"
            )
            logger.info("[WS] ConnectionManager initialized with Redis pub/sub")
        except asyncio.TimeoutError:
            logger.error("[WS] Redis connection timeout during init")
            raise
        except Exception as e:
            logger.error(f"[WS] Redis init failed: {e}")
            raise

    async def shutdown(self):
        """Graceful shutdown — close all connections and cancel listener."""
        # Cancel listener
        if self._listener_task and not self._listener_task.done():
            self._listener_task.cancel()
            try:
                await self._listener_task
            except asyncio.CancelledError:
                pass

        # Close pubsub
        if self._pubsub:
            try:
                await self._pubsub.unsubscribe()
                await self._pubsub.close()
            except Exception:
                pass

        # Close all connections
        async with self._lock:
            for room in self._rooms.values():
                for ws in room.all_websockets:
                    try:
                        await ws.close(code=1001, reason="Server shutting down")
                    except Exception:
                        pass
            self._rooms.clear()
            self._user_ws.clear()
            self._user_rooms.clear()

        logger.info("[WS] ConnectionManager shut down")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    #  Player Connection Lifecycle
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    async def connect_player(self, user_id: str, websocket: WebSocket):
        """
        Accept and register a player's WebSocket connection.
        If the user already has an active WS, close the old one
        (single-session enforcement).
        """
        await websocket.accept()
        old_ws = None

        async with self._lock:
            old_ws = self._user_ws.get(user_id)
            self._user_ws[user_id] = websocket
            if user_id not in self._user_rooms:
                self._user_rooms[user_id] = set()

        # Close old connection OUTSIDE lock (I/O)
        if old_ws:
            try:
                await old_ws.close(code=4001, reason="New connection established")
            except Exception:
                pass

        logger.info(f"[WS] Player {user_id} connected")

    async def disconnect_player(self, user_id: str):
        """
        Remove a player from all rooms and notify room members.
        Called on WebSocketDisconnect or unrecoverable error.
        """
        rooms_to_notify: list[str] = []

        async with self._lock:
            ws = self._user_ws.pop(user_id, None)
            room_ids = self._user_rooms.pop(user_id, set())

            for room_id in room_ids:
                room = self._rooms.get(room_id)
                if room:
                    room.players.pop(user_id, None)
                    rooms_to_notify.append(room_id)
                    if room.is_empty:
                        del self._rooms[room_id]

        # Notify remaining room members OUTSIDE lock
        for room_id in rooms_to_notify:
            await self._publish(room_id, WSEvent.SPECTATOR_UPDATE, {
                "type": "player_disconnected",
                "user_id": user_id,
            })

        logger.info(f"[WS] Player {user_id} disconnected from {len(rooms_to_notify)} room(s)")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    #  Room Management
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    async def join_room(self, room_id: str, user_id: str):
        """
        Add a player to a battle room (called when match_found).
        Subscribes the room's Redis channel for cross-instance events.
        """
        async with self._lock:
            ws = self._user_ws.get(user_id)
            if not ws:
                return

            if room_id not in self._rooms:
                self._rooms[room_id] = BattleRoom(room_id=room_id)

            self._rooms[room_id].players[user_id] = ws
            self._user_rooms.setdefault(user_id, set()).add(room_id)

        # Subscribe Redis channel (idempotent)
        await self._subscribe(room_id)

        logger.info(f"[WS] Player {user_id} joined room {room_id}")

    async def leave_room(self, room_id: str, user_id: str):
        """Remove a player from a room."""
        async with self._lock:
            room = self._rooms.get(room_id)
            if room:
                room.players.pop(user_id, None)
                if room.is_empty:
                    del self._rooms[room_id]

            user_rooms = self._user_rooms.get(user_id)
            if user_rooms:
                user_rooms.discard(room_id)

        logger.debug(f"[WS] Player {user_id} left room {room_id}")

    async def add_spectator(self, room_id: str, websocket: WebSocket):
        """
        Add a spectator to a battle room.
        Spectators receive all broadcasts but cannot send events.
        Returns room info dict, or None if room doesn't exist.
        """
        await websocket.accept()

        async with self._lock:
            if room_id not in self._rooms:
                self._rooms[room_id] = BattleRoom(room_id=room_id)

            room = self._rooms[room_id]
            room.spectators.add(websocket)
            info = room.info()

        # Subscribe Redis channel
        await self._subscribe(room_id)

        logger.info(f"[WS] Spectator joined room {room_id} (total: {info['spectator_count']})")
        return info

    async def remove_spectator(self, room_id: str, websocket: WebSocket):
        """Remove a spectator from a room."""
        async with self._lock:
            room = self._rooms.get(room_id)
            if room:
                room.spectators.discard(websocket)
                if room.is_empty:
                    del self._rooms[room_id]

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    #  Messaging
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    async def send_to_user(self, user_id: str, event: str, data: dict):
        """
        Send a message directly to a specific user (not broadcast).
        
        PRODUCTION: Handles stale connections gracefully.
        """
        async with self._lock:
            ws = self._user_ws.get(user_id)

        if not ws:
            logger.warning(f"[WS] send_to_user: user {user_id} not connected (event={event})")
            return

        try:
            await ws.send_json({"event": event, "data": data})
        except Exception as e:
            logger.warning(f"[WS] Failed to send to user {user_id} (event={event}): {e}", exc_info=True)
            # Clean up stale connection
            await self.disconnect_player(user_id)

    async def is_user_connected(self, user_id: str) -> bool:
        """Whether a player currently has an active WS connection."""
        async with self._lock:
            return user_id in self._user_ws

    async def get_connected_user_ids(self) -> list[str]:
        """Snapshot of currently connected user IDs."""
        async with self._lock:
            return list(self._user_ws.keys())

    async def is_user_in_room(self, room_id: str, user_id: str) -> bool:
        """Whether a user is currently joined as a player in a given room."""
        async with self._lock:
            room = self._rooms.get(room_id)
            return bool(room and user_id in room.players)

    async def broadcast_to_room(self, room_id: str, event: str, data: dict):
        """
        Broadcast an event to everyone in a room:
          1. Local connections (this pod)
          2. Redis PUBLISH (other pods pick it up)
        """
        await self._dispatch_local(room_id, event, data)
        await self._publish(room_id, event, data)

    async def broadcast_to_room_except(
        self, room_id: str, event: str, data: dict, exclude_user_id: str
    ):
        """Broadcast to a room but skip one user (e.g., send opponent_submitted)."""
        message = {"event": event, "data": data}

        async with self._lock:
            room = self._rooms.get(room_id)
            if not room:
                return
            targets = [
                (uid, ws) for uid, ws in room.players.items()
                if uid != exclude_user_id
            ]
            spectators = list(room.spectators)

        # Send outside lock
        for uid, ws in targets:
            try:
                await ws.send_json(message)
            except Exception:
                await self.disconnect_player(uid)

        for ws in spectators:
            try:
                await ws.send_json(message)
            except Exception:
                pass

    async def broadcast_submission_result(
        self,
        room_id: str,
        submitter_id: str,
        verdict: str,
        passed: int,
        total: int,
        runtime_ms: Optional[int],
        memory_kb: Optional[int],
        submission_id: str,
    ):
        """
        Specialized broadcast for submission results.
        Sends detailed result to the submitter, redacted result to opponent + spectators.
        """
        # Full result → submitter
        await self.send_to_user(submitter_id, WSEvent.SUBMISSION_RESULT, {
            "submission_id": submission_id,
            "verdict": verdict,
            "passed": passed,
            "total": total,
            "runtime_ms": runtime_ms,
            "memory_kb": memory_kb,
        })

        # Redacted result → opponent + spectators
        await self.broadcast_to_room_except(
            room_id, WSEvent.OPPONENT_SUBMITTED,
            {"verdict": verdict, "user_id": submitter_id},
            exclude_user_id=submitter_id,
        )

    async def broadcast_match_ended(self, room_id: str, result_data: dict):
        """
        Send match_ended to all room members with personalized ELO deltas.
        result_data must contain: player1_id, player2_id, winner_id,
        player1_elo_delta, player2_elo_delta, player1_new_elo, player2_new_elo, reason.
        """
        p1_id = result_data["player1_id"]
        p2_id = result_data["player2_id"]

        # Player 1's view
        await self.send_to_user(p1_id, WSEvent.MATCH_ENDED, {
            "winner_id": result_data.get("winner_id"),
            "winner_username": result_data.get("winner_username"),
            "reason": result_data["reason"],
            "your_elo_delta": result_data["player1_elo_delta"],
            "new_elo": result_data["player1_new_elo"],
        })

        # Player 2's view
        await self.send_to_user(p2_id, WSEvent.MATCH_ENDED, {
            "winner_id": result_data.get("winner_id"),
            "winner_username": result_data.get("winner_username"),
            "reason": result_data["reason"],
            "your_elo_delta": result_data["player2_elo_delta"],
            "new_elo": result_data["player2_new_elo"],
        })

        # Spectators get a neutral view
        async with self._lock:
            room = self._rooms.get(room_id)
            spectators = list(room.spectators) if room else []

        neutral = {
            "winner_id": result_data.get("winner_id"),
            "reason": result_data["reason"],
        }
        for ws in spectators:
            try:
                await ws.send_json({"event": WSEvent.MATCH_ENDED, "data": neutral})
            except Exception:
                pass

        # Clean up room after match ends
        await self._cleanup_room(room_id)

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    #  Introspection
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    async def get_room_info(self, room_id: str) -> Optional[dict]:
        """Get metadata about a room (for admin/debug endpoints)."""
        async with self._lock:
            room = self._rooms.get(room_id)
            return room.info() if room else None

    async def get_active_rooms(self) -> list[dict]:
        """List all active rooms with metadata."""
        async with self._lock:
            return [room.info() for room in self._rooms.values()]

    async def get_connected_user_count(self) -> int:
        """Number of currently connected players."""
        async with self._lock:
            return len(self._user_ws)

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    #  Internal — local dispatch
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    async def _dispatch_local(self, room_id: str, event: str, data: dict):
        """
        Send to all local connections in a room.
        Collects targets under lock, sends outside lock.
        """
        message = {"event": event, "data": data}

        async with self._lock:
            room = self._rooms.get(room_id)
            if not room:
                return
            targets = list(room.all_websockets)

        dead: list[WebSocket] = []
        for ws in targets:
            try:
                await ws.send_json(message)
            except Exception:
                dead.append(ws)

        # Purge dead connections
        if dead:
            async with self._lock:
                room = self._rooms.get(room_id)
                if room:
                    for ws in dead:
                        room.spectators.discard(ws)
                        # Also remove from players if needed
                        dead_uids = [
                            uid for uid, w in room.players.items() if w in dead
                        ]
                        for uid in dead_uids:
                            room.players.pop(uid, None)

    async def _cleanup_room(self, room_id: str):
        """Remove a room and all its connections after match ends."""
        async with self._lock:
            room = self._rooms.pop(room_id, None)
            if room:
                for uid in room.players:
                    user_rooms = self._user_rooms.get(uid)
                    if user_rooms:
                        user_rooms.discard(room_id)

        # Unsubscribe Redis channel
        if self._pubsub:
            try:
                await self._pubsub.unsubscribe(RedisKey.ws_channel(room_id))
            except Exception:
                pass

        logger.info(f"[WS] Room {room_id} cleaned up")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    #  Internal — Redis pub/sub (cross-instance)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    async def _publish(self, room_id: str, event: str, data: dict):
        """Publish an event to Redis for other pods to pick up."""
        if not self._redis:
            return
        payload = json.dumps({
            "event": event,
            "data": data,
            "source": self._instance_id,  # Echo guard
        })
        try:
            await self._redis.publish(RedisKey.ws_channel(room_id), payload)
        except Exception as e:
            logger.error(f"[WS] Redis publish error: {e}")

    async def _subscribe(self, room_id: str):
        """Subscribe to a room's Redis channel (idempotent)."""
        if not self._pubsub:
            return
        channel = RedisKey.ws_channel(room_id)
        try:
            await self._pubsub.subscribe(channel)
        except Exception as e:
            logger.error(f"[WS] Redis subscribe error for {room_id}: {e}")

    async def _redis_listener(self):
        """
        Long-running task that listens for Redis pub/sub messages
        and dispatches them to local connections.

        PRODUCTION: Auto-reconnects on failure, handles stale connections.
        The source_instance_id guard prevents echo (this pod broadcasting
        a message, then receiving it back via Redis and sending it again).
        """
        if not self._pubsub:
            return

        logger.info("[WS] Redis pub/sub listener started")
        reconnect_delay = 1
        max_reconnect_delay = 30

        while True:
            try:
                async for message in self._pubsub.listen():
                    # Reset reconnect delay on successful message
                    reconnect_delay = 1
                    
                    if message["type"] != "message":
                        continue

                    channel = message["channel"]
                    if isinstance(channel, bytes):
                        channel = channel.decode()

                    raw = message["data"]
                    if isinstance(raw, bytes):
                        raw = raw.decode()

                    try:
                        payload = json.loads(raw)
                    except json.JSONDecodeError:
                        logger.debug(f"[WS] Invalid JSON in pub/sub message: {raw[:100]}")
                        continue

                    # Echo guard: skip messages we published ourselves
                    if payload.get("source") == self._instance_id:
                        continue

                    event = payload.get("event")
                    data = payload.get("data", {})

                    # Extract room_id: channel is "ws:match:{match_id}"
                    room_id = channel.replace("ws:match:", "")

                    await self._dispatch_local(room_id, event, data)

            except asyncio.CancelledError:
                logger.info("[WS] Redis listener cancelled")
                break
            except Exception as e:
                logger.error(f"[WS] Redis listener error: {e} — reconnecting in {reconnect_delay}s")
                await asyncio.sleep(reconnect_delay)
                
                # Exponential backoff with cap
                reconnect_delay = min(reconnect_delay * 2, max_reconnect_delay)
                
                # Recreate pubsub connection if needed
                if self._redis:
                    try:
                        if self._pubsub:
                            try:
                                await self._pubsub.close()
                            except Exception:
                                pass
                        self._pubsub = self._redis.pubsub()
                        # Re-subscribe to all active rooms
                        async with self._lock:
                            for room_id in self._rooms.keys():
                                await self._subscribe(room_id)
                    except Exception as reconnect_error:
                        logger.error(f"[WS] Failed to reconnect pubsub: {reconnect_error}")
                        # If Redis is completely down, break and let system handle it
                        if not await self._test_redis_connection():
                            logger.error("[WS] Redis connection lost, stopping listener")
                            break

    async def _test_redis_connection(self) -> bool:
        """Test if Redis connection is alive."""
        if not self._redis:
            return False
        try:
            await asyncio.wait_for(self._redis.ping(), timeout=2)
            return True
        except Exception:
            return False


# ── Singleton ─────────────────────────────────────────────────
manager = ConnectionManager()
