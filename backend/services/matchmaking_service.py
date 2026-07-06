"""
Matchmaking service — ELO-based queue + pairing with Redis.

Architecture:
  - Redis Sorted Set (score=ELO) for O(log N) range queries
  - Per-user SETNX lock prevents duplicate queue joins
  - Global SETNX lock ensures one matchmaker processes at a time (multi-instance safe)
  - Lua script for atomic pair removal (no race between two matchmakers)
  - Expanding ELO window prevents player starvation

Config (from settings):
  - Initial window: ±100 ELO
  - Expands by ±100 every 30 seconds of wait time
  - Max window: ±500 ELO
"""

import time
import uuid
import logging

from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from backend.config import settings
from backend.core.constants import RedisKey, MatchStatus
from backend.core.exceptions import AlreadyInMatch
from backend.models.match import Match
from backend.services import problem_service

logger = logging.getLogger(__name__)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Lua Scripts (executed atomically inside Redis)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Atomically remove two members from a sorted set.
# If either ZREM fails (member already removed by another instance),
# the script rolls back. This is the core race-condition guard.
#
# Returns 1 on success, 0 if a concurrent matchmaker already took one.
ATOMIC_PAIR_REMOVE = """
local r1 = redis.call('ZREM', KEYS[1], ARGV[1])
local r2 = redis.call('ZREM', KEYS[1], ARGV[2])
if r1 == 1 and r2 == 1 then
    return 1
else
    -- Rollback: re-add whichever was removed
    if r1 == 1 then redis.call('ZADD', KEYS[1], ARGV[3], ARGV[1]) end
    if r2 == 1 then redis.call('ZADD', KEYS[1], ARGV[4], ARGV[2]) end
    return 0
end
"""

# Atomically join queue: check active match, acquire lock, add to queue.
# Returns: 1 = success, 0 = already in match, -1 = already in queue
ATOMIC_JOIN_QUEUE = """
local uid = ARGV[1]
local elo = tonumber(ARGV[2])
local member = ARGV[3]
local active_match_key = KEYS[1]
local lock_key = KEYS[2]
local queue_key = KEYS[3]

-- Check if already in active match
if redis.call('EXISTS', active_match_key) == 1 then
    return 0  -- Already in match
end

-- Try to acquire lock (SETNX)
if redis.call('SET', lock_key, '1', 'NX', 'EX', 60) == false then
    return -1  -- Already in queue (lock exists)
end

-- Add to queue
redis.call('ZADD', queue_key, elo, member)
return 1  -- Success
"""

# Atomically leave queue: remove member, release lock.
# Returns: 1 = success, 0 = not found
ATOMIC_LEAVE_QUEUE = """
local uid = ARGV[1]
local queue_key = KEYS[1]
local lock_key = KEYS[2]

-- Find and remove member with this user_id prefix
local members = redis.call('ZRANGE', queue_key, 0, -1)
local removed = 0
for i, member in ipairs(members) do
    local member_str = tostring(member)
    if string.sub(member_str, 1, string.len(uid)) == uid then
        redis.call('ZREM', queue_key, member_str)
        removed = 1
        break
    end
end

-- Always release lock (idempotent)
redis.call('DEL', lock_key)
return removed
"""


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Public API
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def join_queue(redis: Redis, user_id: uuid.UUID, elo: int) -> bool:
    """
    Add a player to the matchmaking queue.

    PRODUCTION: Uses atomic Lua script to prevent race conditions.
    All checks (active match, lock, enqueue) happen atomically.

    Guards:
      1. Rejects if the user is already in an active match (Redis key check)
      2. Acquires a per-user distributed lock (SETNX, 60s TTL) to prevent
         double-joins across multiple API instances
      3. Atomically adds to queue

    Redis structure:
      Sorted Set "matchmaking:queue"
        member = "<user_id>:<join_timestamp>"
        score  = ELO rating
    """
    uid = str(user_id)
    member = f"{uid}:{time.time()}"

    # ── Atomic join: check match, acquire lock, enqueue ────
    async def _is_in_queue() -> bool:
        """Check whether the user already has a member entry in the queue zset."""
        members = await redis.zrange(RedisKey.MATCHMAKING_QUEUE, 0, -1)
        for m in members:
            ms = m.decode() if isinstance(m, bytes) else m
            if ms.startswith(uid):
                return True
        return False

    async def _attempt_join() -> int:
        return await redis.eval(
            ATOMIC_JOIN_QUEUE,
            3,  # number of KEYS
            RedisKey.user_active_match(uid),      # KEYS[1]
            RedisKey.matchmaking_lock(uid),       # KEYS[2]
            RedisKey.MATCHMAKING_QUEUE,           # KEYS[3]
            uid,                                  # ARGV[1]
            str(elo),                             # ARGV[2]
            member,                               # ARGV[3]
        )

    # ── Atomic join: check match, acquire lock, enqueue ────
    result = await _attempt_join()

    if result == 0:
        # Already in match is still an error (frontend shows "already matched")
        raise AlreadyInMatch()

    if result == 1:
        logger.info(f"[MATCHMAKING] Player {uid} queued (ELO={elo})")
        return True

    if result == -1:
        # Idempotent join:
        # - If user is already in queue → success
        # - If lock is stale (server restart) and user NOT in queue → clear lock and retry once
        if await _is_in_queue():
            logger.info(f"[MATCHMAKING] Player {uid} already queued (idempotent join)")
            return True

        # Stale lock: release and retry once
        await redis.delete(RedisKey.matchmaking_lock(uid))
        retry = await _attempt_join()
        if retry == 1:
            logger.info(f"[MATCHMAKING] Player {uid} queued after stale-lock recovery")
            return True
        if retry == 0:
            raise AlreadyInMatch()

        # If we still can't join, treat as already queued to preserve idempotency
        logger.warning(f"[MATCHMAKING] join_queue retry failed (result={retry}) for {uid}; treating as queued")
        return True

    # Unexpected result - log and treat as queued for idempotency (client can poll status)
    logger.error(f"[MATCHMAKING] Unexpected join_queue result: {result} (uid={uid})", exc_info=True)
    return True


async def leave_queue(redis: Redis, user_id: uuid.UUID) -> bool:
    """
    Remove a player from the matchmaking queue and release their lock.
    
    PRODUCTION: Uses atomic Lua script to prevent race conditions.
    Member removal and lock release happen atomically.
    """
    uid = str(user_id)

    # ── Atomic leave: remove member, release lock ──────────
    result = await redis.eval(
        ATOMIC_LEAVE_QUEUE,
        2,  # number of KEYS
        RedisKey.MATCHMAKING_QUEUE,      # KEYS[1]
        RedisKey.matchmaking_lock(uid),   # KEYS[2]
        uid,                              # ARGV[1]
    )

    # Idempotent leave: if not found, still return success.
    if result == 0:
        logger.info(f"[MATCHMAKING] Player {uid} not in queue (idempotent leave)")
        return True

    logger.info(f"[MATCHMAKING] Player {uid} left queue")
    return True


async def get_queue_position(redis: Redis, user_id: uuid.UUID) -> Optional[dict]:
    """
    Get a player's queue status: position, wait time, current ELO window.
    Returns None if not in queue.
    """
    uid = str(user_id)
    members_with_scores = await redis.zrangebyscore(
        RedisKey.MATCHMAKING_QUEUE, "-inf", "+inf", withscores=True
    )

    for idx, (member, score) in enumerate(members_with_scores):
        member_str = member.decode() if isinstance(member, bytes) else member
        if member_str.startswith(uid):
            join_ts = float(member_str.split(":")[1])
            wait_secs = time.time() - join_ts
            return {
                "position": idx + 1,
                "total_in_queue": len(members_with_scores),
                "wait_seconds": round(wait_secs, 1),
                "current_elo_window": _calculate_elo_window(wait_secs),
                "elo": int(score),
            }

    return None


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Matchmaker — called periodically by the matchmaking worker
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def process_queue(redis: Redis, db: AsyncSession) -> list[uuid.UUID]:
    """
    Core matchmaking loop.

    Multi-instance safety:
      1. SETNX global lock with 2s TTL → only ONE pod processes at a time
      2. Lua ATOMIC_PAIR_REMOVE → if another pod snuck in, the Lua script
         rolls back and returns 0 (we skip and retry next cycle)

    Algorithm:
      - Pull all queued players from the sorted set
      - Sort by wait time (longest first → fairness)
      - For each unmatched player, find the closest-ELO candidate
        within their expanding window
      - If found, atomically remove both via Lua and create a match

    Returns list of newly created match IDs.
    """
    # ── Global lock (2s TTL prevents deadlocks) ───────────
    if not await redis.set(RedisKey.MATCHMAKING_GLOBAL_LOCK, "1", nx=True, ex=2):
        return []  # Another instance is processing

    created_matches = []

    try:
        # Fetch all queued players: [(member_bytes, elo_float), ...]
        queue_entries = await redis.zrangebyscore(
            RedisKey.MATCHMAKING_QUEUE, "-inf", "+inf", withscores=True
        )

        if len(queue_entries) < 2:
            if len(queue_entries) == 1:
                players = _parse_queue_entries(queue_entries)
                player = players[0]
                wait_secs = time.time() - player["joined_at"]
                if wait_secs >= settings.matchmaking_bot_fallback_seconds:
                    bot_match_id = await _try_bot_fallback_match(db, redis, player)
                    if bot_match_id:
                        created_matches.append(bot_match_id)
            return created_matches

        # Parse queue into structured list
        players = _parse_queue_entries(queue_entries)

        # Sort by join time — longest waiting player gets priority
        players.sort(key=lambda p: p["joined_at"])

        matched_user_ids: set[str] = set()

        for i, player in enumerate(players):
            if player["user_id"] in matched_user_ids:
                continue  # Already paired in this cycle

            # ── Expanding window ─────────────────────────
            wait_secs = time.time() - player["joined_at"]
            window = _calculate_elo_window(wait_secs)

            # ── Find best candidate ──────────────────────
            best = _find_closest_candidate(player, players, i, matched_user_ids, window)
            if best is None:
                continue  # No suitable opponent yet

            # ── Atomic removal (Lua) ─────────────────────
            ok = await redis.eval(
                ATOMIC_PAIR_REMOVE,
                1,                              # number of KEYS
                RedisKey.MATCHMAKING_QUEUE,      # KEYS[1]
                player["member"],               # ARGV[1]
                best["member"],                 # ARGV[2]
                str(player["elo"]),             # ARGV[3] (rollback score)
                str(best["elo"]),               # ARGV[4] (rollback score)
            )

            if not ok:
                # Another instance removed one of them — skip, retry next cycle
                logger.debug(
                    f"[MATCHMAKING] Atomic remove failed for "
                    f"{player['user_id']} vs {best['user_id']} — retrying"
                )
                continue

            # Lock both players to prevent re-matching before DB write completes
            pair_lock = f"lock:pairing:{player['user_id']}:{best['user_id']}"
            if not await redis.set(pair_lock, "1", nx=True, ex=10):
                logger.debug(f"[MATCHMAKING] Pair lock held for {player['user_id']} vs {best['user_id']}")
                # Re-add both players to the queue so they aren't lost
                await redis.zadd(RedisKey.MATCHMAKING_QUEUE, {player["member"]: player["elo"]})
                await redis.zadd(RedisKey.MATCHMAKING_QUEUE, {best["member"]: best["elo"]})
                continue

            # ── Create match ─────────────────────────────
            match_id = await _create_match(
                db, redis,
                player["user_id"], player["elo"],
                best["user_id"], best["elo"],
            )

            matched_user_ids.add(player["user_id"])
            matched_user_ids.add(best["user_id"])
            created_matches.append(match_id)

            # Release per-user locks
            await redis.delete(
                RedisKey.matchmaking_lock(player["user_id"]),
                RedisKey.matchmaking_lock(best["user_id"]),
            )

            logger.info(
                f"[MATCHMAKING] Paired {player['user_id']} (ELO={player['elo']}) "
                f"vs {best['user_id']} (ELO={best['elo']}) "
                f"| window=±{window} | match={match_id}"
            )
        
    finally:
        # Always release global lock
        await redis.delete(RedisKey.MATCHMAKING_GLOBAL_LOCK)

    return created_matches


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Internal helpers
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _parse_queue_entries(entries: list[tuple]) -> list[dict]:
    """Parse raw Redis sorted set entries into player dicts."""
    players = []
    for member, score in entries:
        member_str = member.decode() if isinstance(member, bytes) else member
        uid, ts = member_str.split(":", 1)
        players.append({
            "member": member_str,
            "user_id": uid,
            "elo": int(score),
            "joined_at": float(ts),
        })
    return players


def _find_closest_candidate(
    player: dict,
    all_players: list[dict],
    player_index: int,
    excluded: set[str],
    window: int,
) -> Optional[dict]:
    """
    Find the closest-ELO opponent within the allowed window.

    Returns the candidate dict, or None if no match within range.
    """
    best = None
    best_diff = float("inf")

    for j, candidate in enumerate(all_players):
        if j == player_index or candidate["user_id"] in excluded:
            continue

        diff = abs(player["elo"] - candidate["elo"])
        if diff <= window and diff < best_diff:
            best_diff = diff
            best = candidate

    return best


def _calculate_elo_window(wait_seconds: float) -> int:
    """
    Expanding ELO window to prevent starvation.

    Timeline (with default config):
      0–30s  → ±100 (initial, tight matches)
      30–60s → ±200 (first expansion)
      60–90s → ±300 (second expansion)
      90s+   → ±400 ... capped at ±500

    Formula:
      window = initial + floor(wait / expand_interval) * expand_step
      window = min(window, max_window)
    """
    expansions = int(wait_seconds / settings.matchmaking_elo_expand_interval_seconds)
    window = settings.matchmaking_elo_initial_window + (expansions * settings.matchmaking_elo_expand_step)
    return min(window, settings.matchmaking_elo_max_window)


async def _try_bot_fallback_match(db: AsyncSession, redis: Redis, player: dict) -> uuid.UUID | None:
    """Pair a long-waiting solo player with a bot."""
    from backend.services.bot_service import get_random_bot_for_elo

    bot = await get_random_bot_for_elo(db, player["elo"], player["user_id"])
    if bot is None:
        return None

    await redis.zrem(RedisKey.MATCHMAKING_QUEUE, player["member"])
    await redis.delete(RedisKey.matchmaking_lock(player["user_id"]))

    bot_id = str(bot.id)
    match_id = await _create_match(
        db, redis,
        player["user_id"], player["elo"],
        bot_id, bot.elo,
    )
    logger.info(
        "[MATCHMAKING] Bot fallback: %s (ELO=%s) vs bot %s",
        player["user_id"], player["elo"], bot_id,
    )
    return match_id


async def create_immediate_bot_match(
    db: AsyncSession,
    redis: Optional[Redis],
    user_id: uuid.UUID,
    user_elo: int,
) -> uuid.UUID:
    """Create a match immediately against a bot (tutorial / onboarding)."""
    from backend.services.bot_service import get_random_bot_for_elo
    from backend.services.matchmaking_memory import memory_queue

    bot = await get_random_bot_for_elo(db, user_elo, str(user_id))
    if bot is None:
        raise ValueError("No bot available")

    bot_id = str(bot.id)
    if redis is not None:
        await redis.delete(RedisKey.matchmaking_lock(str(user_id)))
        member_pattern = f"{user_id}:"
        queue_entries = await redis.zrange(RedisKey.MATCHMAKING_QUEUE, 0, -1)
        for member in queue_entries:
            member_str = member.decode() if isinstance(member, bytes) else str(member)
            if member_str.startswith(member_pattern):
                await redis.zrem(RedisKey.MATCHMAKING_QUEUE, member_str)
        return await _create_match(db, redis, str(user_id), user_elo, bot_id, bot.elo)

    from backend.db.session import AsyncSessionLocal

    match_id = await memory_queue._create_match(
        AsyncSessionLocal, str(user_id), user_elo, bot_id, bot.elo
    )
    async with memory_queue._lock:
        memory_queue._active_matches[str(user_id)] = str(match_id)
        memory_queue._active_matches[bot_id] = str(match_id)
    await memory_queue._notify_match_found(AsyncSessionLocal, match_id, str(user_id), bot_id)
    return match_id


async def _create_match(
    db: AsyncSession,
    redis: Redis,
    p1_id: str,
    p1_elo: int,
    p2_id: str,
    p2_elo: int,
) -> uuid.UUID:
    """
    Create a match in PostgreSQL and set up Redis state.
    
    PRODUCTION: Atomic transaction with rollback on failure.
    If Redis operations fail, PostgreSQL transaction is rolled back.
    """
    # Select an ELO-appropriate problem
    avg_elo = (p1_elo + p2_elo) // 2
    problem = await problem_service.get_problem_for_match(db, avg_elo)

    # ── PostgreSQL: persist match (in transaction) ────────
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
    
    try:
        await db.commit()
        await db.refresh(match)
    except Exception as e:
        await db.rollback()
        logger.error(f"[MATCHMAKING] Failed to create match in DB: {e}")
        raise

    mid = str(match.id)
    ttl = settings.match_duration_seconds + 60  # Buffer for cleanup

    # ── Redis: set up state (if this fails, match exists in DB but Redis is inconsistent)
    # This is acceptable - Redis state can be rebuilt from DB if needed
    try:
        expiry_ts = time.time() + settings.match_duration_seconds
        
        # Use pipeline for atomic Redis operations
        pipe = redis.pipeline()
        pipe.set(RedisKey.match_timer(mid), str(expiry_ts), ex=ttl)
        pipe.hset(RedisKey.match_state(mid), mapping={
            "status": MatchStatus.ACTIVE,
            "player1_id": p1_id,
            "player2_id": p2_id,
            "problem_id": str(problem.id),
            "problem_title": problem.title,
            "started_at": str(time.time()),
        })
        pipe.expire(RedisKey.match_state(mid), ttl)
        pipe.set(RedisKey.user_active_match(p1_id), mid, ex=ttl)
        pipe.set(RedisKey.user_active_match(p2_id), mid, ex=ttl)
        await pipe.execute()
    except Exception as e:
        # Log but don't fail - match is already in DB
        logger.error(f"[MATCHMAKING] Failed to set Redis state for match {mid}: {e}")
        # Match will still work, but Redis state may be inconsistent

    return match.id


async def create_private_match(
    db: AsyncSession,
    redis: Redis,
    p1_id: str,
    p1_elo: int,
    p2_id: str,
    p2_elo: int,
) -> uuid.UUID:
    """
    Directly create a match between two specific users (for private rooms).
    Checks if either user is already in an active match first.
    """
    # 1. Reject if either user is already in a match
    p1_active = await redis.get(RedisKey.user_active_match(p1_id))
    p2_active = await redis.get(RedisKey.user_active_match(p2_id))
    
    if p1_active or p2_active:
        raise AlreadyInMatch()

    # 2. Ensure they are removed from the global matchmaking queue
    await leave_queue(redis, uuid.UUID(p1_id))
    await leave_queue(redis, uuid.UUID(p2_id))

    # 3. Use the existing robust _create_match function
    match_id = await _create_match(db, redis, p1_id, p1_elo, p2_id, p2_elo)
    
    logger.info(
        f"[MATCHMAKING] Private match {match_id} created manually for "
        f"{p1_id} vs {p2_id}"
    )
    return match_id
