"""
In-memory matchmaking — dev-mode fallback when Redis is disabled.

Fully atomic implementation:
  - Global singleton queue (dict keyed by user_id)
  - Background poller (process_queue runs every 500ms)
  - ELO window matching (same algorithm as Redis version)
  - PostgreSQL match creation
  - WebSocket match_found notification to both players
  - Atomic state transitions under a single lock

Limitations vs Redis-backed:
  - Single process only (no cross-instance sync)
  - No persistence across restarts
"""

import time
import uuid
import logging
import asyncio
from dataclasses import dataclass, field

from sqlalchemy.ext.asyncio import async_sessionmaker

from backend.config import settings
from backend.core.constants import MatchStatus


logger = logging.getLogger(__name__)


@dataclass
class QueueEntry:
    user_id: str
    elo: int
    joined_at: float = field(default_factory=time.time)


class InMemoryMatchmakingQueue:
    """Singleton in-memory matchmaking with background pairing."""

    def __init__(self):
        self._queue: dict[str, QueueEntry] = {}       # user_id → entry
        self._lock = asyncio.Lock()
        self._active_matches: dict[str, str] = {}     # user_id → match_id
        self._pending_pair: set[str] = set()           # being paired right now

    # ── Public API ────────────────────────────────────────

    async def join_queue(self, user_id: uuid.UUID, elo: int) -> dict:
        """
        Add user to queue.
        Returns:
          {"status": "queued"}            — freshly queued
          {"status": "already_matched", "match_id": "..."}  — already in a live match
        Raises AlreadyInQueue only if truly duplicate-queued.
        """
        uid = str(user_id)
        async with self._lock:
            # Already in an active match → return match info (not an error)
            if uid in self._active_matches:
                mid = self._active_matches[uid]
                logger.info(f"[MM-DEV] Player {uid} already matched → {mid}")
                return {"status": "already_matched", "match_id": mid}

            # Currently being paired by poller → treat as in-queue
            if uid in self._pending_pair:
                logger.info(f"[MM-DEV] Player {uid} is being paired, skipping re-add")
                return {"status": "queued"}

            # Already in queue → idempotent (don't 409)
            if uid in self._queue:
                logger.info(f"[MM-DEV] Player {uid} already in queue, idempotent")
                return {"status": "queued"}

            self._queue[uid] = QueueEntry(user_id=uid, elo=elo)
            size = len(self._queue)

        logger.info(
            f"[MM-DEV] Player {uid} joined queue (ELO={elo}). "
            f"Queue size: {size}"
        )
        return {"status": "queued"}

    async def leave_queue(self, user_id: uuid.UUID) -> bool:
        """
        Idempotent removal from any pre-match state.

        Requirements:
          - Never raise NotInQueue (idempotent)
          - Remove from _queue and _pending_pair
          - Remove from _active_matches only if clearly stale/safe
        """
        uid = str(user_id)

        # Phase 1: remove from queue + pending atomically
        maybe_match_id = None
        removed_from_queue = False
        removed_from_pending = False

        async with self._lock:
            if uid in self._queue:
                self._queue.pop(uid, None)
                removed_from_queue = True
            if uid in self._pending_pair:
                self._pending_pair.discard(uid)
                removed_from_pending = True
            maybe_match_id = self._active_matches.get(uid)
            size = len(self._queue)

        # Phase 2: (optional) clear stale active match mapping if safe
        if maybe_match_id:
            try:
                from backend.websocket.manager import manager
                info = await manager.get_room_info(maybe_match_id)
                if info is None:
                    async with self._lock:
                        # Only clear if unchanged
                        if self._active_matches.get(uid) == maybe_match_id:
                            self._active_matches.pop(uid, None)
                    logger.info(
                        f"[MM-DEV] Cleared stale active match mapping for {uid} → {maybe_match_id}"
                    )
            except Exception as e:
                logger.debug(f"[MM-DEV] leave_queue stale-active cleanup skipped: {e}")

        if removed_from_queue or removed_from_pending:
            logger.info(
                f"[MM-DEV] Player {uid} left matchmaking state "
                f"(queue={removed_from_queue}, pending={removed_from_pending}). "
                f"Queue size: {size}"
            )
        else:
            logger.info(f"[MM-DEV] Player {uid} not in queue (idempotent leave). Queue size: {size}")

        return True

    async def get_queue_position(self, user_id: uuid.UUID) -> dict | None:
        uid = str(user_id)
        async with self._lock:
            # Already matched
            if uid in self._active_matches:
                return {
                    "status": "matched",
                    "match_id": self._active_matches[uid],
                }
            if uid not in self._queue:
                return None
            entry = self._queue[uid]
            sorted_entries = sorted(
                self._queue.values(), key=lambda e: e.joined_at
            )
            position = next(
                i + 1 for i, e in enumerate(sorted_entries)
                if e.user_id == uid
            )
            wait_secs = time.time() - entry.joined_at
            window = _calculate_elo_window(wait_secs)
            return {
                "position": position,
                "total_in_queue": len(self._queue),
                "wait_seconds": round(wait_secs, 1),
                "current_elo_window": window,
                "elo": entry.elo,
            }

    async def get_queue_size(self) -> int:
        async with self._lock:
            return len(self._queue)

    # ── Poller-called pairing logic ───────────────────────

    async def process_queue(self, session_factory: async_sessionmaker) -> list[uuid.UUID]:
        """
        Atomic pairing loop:
          1. Under lock: snapshot queue, find pairs, move paired users
             into _pending_pair so they can't be re-joined
          2. Outside lock: create match in DB (slow)
          3. Under lock: move from _pending_pair to _active_matches
        """
        # ── Phase 1: find pairs atomically ────────────────
        async with self._lock:
            if len(self._queue) < 2:
                return []

            players = sorted(self._queue.values(), key=lambda e: e.joined_at)

            pairs: list[tuple[QueueEntry, QueueEntry]] = []
            matched_ids: set[str] = set()

            for i, player in enumerate(players):
                if player.user_id in matched_ids:
                    continue

                wait_secs = time.time() - player.joined_at
                window = _calculate_elo_window(wait_secs)

                best = None
                best_diff = float("inf")

                for j, candidate in enumerate(players):
                    if j == i or candidate.user_id in matched_ids:
                        continue
                    diff = abs(player.elo - candidate.elo)
                    if diff <= window and diff < best_diff:
                        best_diff = diff
                        best = candidate

                if best is not None:
                    pairs.append((player, best))
                    matched_ids.add(player.user_id)
                    matched_ids.add(best.user_id)

            if not pairs:
                return []

            # Atomically: remove from queue, mark as pending
            for p1, p2 in pairs:
                self._queue.pop(p1.user_id, None)
                self._queue.pop(p2.user_id, None)
                self._pending_pair.add(p1.user_id)
                self._pending_pair.add(p2.user_id)

            logger.info(
                f"[MM-DEV] Found {len(pairs)} pair(s), "
                f"removed from queue, marked pending"
            )

        # ── Phase 2: create matches in DB (outside lock) ──
        created: list[uuid.UUID] = []
        for p1, p2 in pairs:
            try:
                match_id = await self._create_match(
                    session_factory, p1.user_id, p1.elo, p2.user_id, p2.elo
                )
                created.append(match_id)

                # ── Phase 3: move pending → active (under lock) ──
                async with self._lock:
                    self._pending_pair.discard(p1.user_id)
                    self._pending_pair.discard(p2.user_id)
                    self._active_matches[p1.user_id] = str(match_id)
                    self._active_matches[p2.user_id] = str(match_id)

                logger.info(
                    f"[MM-DEV] PAIRED: {p1.user_id} (ELO={p1.elo}) "
                    f"vs {p2.user_id} (ELO={p2.elo}) | match={match_id}"
                )

                # Notify both players via WebSocket
                await self._notify_match_found(session_factory, match_id, p1.user_id, p2.user_id)

            except Exception as e:
                # Roll back: remove from pending, don't re-queue (user can re-join)
                async with self._lock:
                    self._pending_pair.discard(p1.user_id)
                    self._pending_pair.discard(p2.user_id)
                logger.error(f"[MM-DEV] Match creation failed: {e}", exc_info=True)

        return created

    async def _create_match(
        self,
        session_factory: async_sessionmaker,
        p1_id: str, p1_elo: int,
        p2_id: str, p2_elo: int,
    ) -> uuid.UUID:
        """Create match in PostgreSQL with a random problem."""
        from backend.services.problem_service import get_random_problem
        from backend.models.match import Match

        async with session_factory() as db:
            problem = await get_random_problem(db)

            match = Match(
                player1_id=uuid.UUID(p1_id),
                player2_id=uuid.UUID(p2_id),
                problem_id=problem.id,
                status=MatchStatus.ACTIVE,
                player1_elo_before=p1_elo,
                player2_elo_before=p2_elo,
                duration_seconds=settings.match_duration_seconds,
            )
            db.add(match)
            await db.commit()
            await db.refresh(match)

            logger.info(
                f"[MM-DEV] Match {match.id} created in DB: "
                f"{p1_id} vs {p2_id} | problem={problem.title}"
            )
            return match.id

    async def _notify_match_found(
        self,
        session_factory: async_sessionmaker,
        match_id: uuid.UUID,
        p1_id: str,
        p2_id: str,
    ) -> None:
        """
        Send match_found event to both players via WebSocket.

        Frontend expects payload:
          {
            "match_id": "...",
            "problem_id": "...",
            "problem_title": "...",
            "player1": { "user_id": "..." },
            "player2": { "user_id": "..." },
            "duration_seconds": ...
          }
        """
        from backend.websocket.manager import manager
        from backend.services.match_service import get_match

        async with session_factory() as db:
            match = await get_match(db, match_id)

        payload = {
            "match_id": str(match.id),
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

        # Notify both players
        await manager.send_to_user(p1_id, "match_found", payload)
        await manager.send_to_user(p2_id, "match_found", payload)

        # Join both players into the match room (lets subsequent room broadcasts work)
        mid = str(match.id)
        await manager.join_room(mid, p1_id)
        await manager.join_room(mid, p2_id)

        logger.info(f"[MM-DEV] match_found sent to {p1_id},{p2_id}; both joined room {mid}")

    def clear_active_match(self, user_id: str):
        """Remove active match tracking (called after match ends)."""
        self._active_matches.pop(user_id, None)

    def clear_match_for_both(self, user1_id: str, user2_id: str) -> None:
        """
        Remove active match tracking for both players.

        This is critical in dev-mode: if `_active_matches` is not cleared after
        match end (solve/forfeit/timeout), players cannot re-queue.
        """
        before_1 = self._active_matches.get(user1_id)
        before_2 = self._active_matches.get(user2_id)
        self._active_matches.pop(user1_id, None)
        self._active_matches.pop(user2_id, None)
        logger.info(
            f"[MM-DEV] Cleaned active_matches for both players: "
            f"{user1_id} ({before_1}) and {user2_id} ({before_2})"
        )


def _calculate_elo_window(wait_seconds: float) -> int:
    expansions = int(wait_seconds / settings.matchmaking_elo_expand_interval_seconds)
    window = settings.matchmaking_elo_initial_window + (
        expansions * settings.matchmaking_elo_expand_step
    )
    return min(window, settings.matchmaking_elo_max_window)


# ── Singleton ─────────────────────────────────────────────────
memory_queue = InMemoryMatchmakingQueue()


# ── Background poller ─────────────────────────────────────────

async def run_matchmaking_poller(session_factory: async_sessionmaker) -> None:
    """
    Background task: poll the in-memory queue every N ms for pairs.
    Started by FastAPI lifespan when Redis is disabled.
    """
    poll_ms = settings.matchmaking_poll_interval_ms
    logger.info(f"[MM-DEV] Matchmaking poller started (poll every {poll_ms}ms)")

    while True:
        try:
            created = await memory_queue.process_queue(session_factory)
            if created:
                logger.info(
                    f"[MM-DEV] Poller created {len(created)} match(es): "
                    f"{[str(m) for m in created]}"
                )
        except asyncio.CancelledError:
            logger.info("[MM-DEV] Matchmaking poller shutting down")
            break
        except Exception as e:
            logger.error(f"[MM-DEV] Poller error: {e}", exc_info=True)

        await asyncio.sleep(poll_ms / 1000.0)
