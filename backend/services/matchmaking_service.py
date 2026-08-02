"""
Matchmaking service — ELO-based queue + pairing with Redis.

Architecture:
  - Redis Sorted Set (score=ELO) for O(log N) range queries
  - Per-user SETNX lock prevents duplicate queue joins
  - Global SETNX lock ensures one matchmaker processes at a time (multi-instance safe)
  - Lua script for atomic pair claim (ZREM + claim, no leave/rejoin window)
  - Expanding ELO window prevents player starvation

Config (from settings):
  - Initial window: ±100 ELO
  - Expands by ±100 every 30 seconds of wait time
  - Max window: ±500 ELO
"""

import time
import uuid
import logging
from datetime import datetime, timezone

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

# Atomically ZREM both players AND set pairing claims (same pattern as
# ATOMIC_BOT_CLAIM). Claim SET after a bare ZREM left a leave/rejoin window.
#
# KEYS: queue, claim1, claim2, member1, member2, lock1, lock2
# ARGV: member1, member2, elo1, elo2, claim_ttl
# Returns 1 on success, 0 if a concurrent matchmaker already took one.
ATOMIC_PAIR_CLAIM = """
local queue_key = KEYS[1]
local claim1_key = KEYS[2]
local claim2_key = KEYS[3]
local member1_key = KEYS[4]
local member2_key = KEYS[5]
local lock1_key = KEYS[6]
local lock2_key = KEYS[7]
local member1 = ARGV[1]
local member2 = ARGV[2]
local elo1 = tonumber(ARGV[3])
local elo2 = tonumber(ARGV[4])
local claim_ttl = tonumber(ARGV[5])

local r1 = redis.call('ZREM', queue_key, member1)
local r2 = redis.call('ZREM', queue_key, member2)
if r1 == 1 and r2 == 1 then
    redis.call('SET', claim1_key, '1', 'EX', claim_ttl)
    redis.call('SET', claim2_key, '1', 'EX', claim_ttl)
    redis.call('DEL', member1_key)
    redis.call('DEL', member2_key)
    redis.call('SET', lock1_key, '1', 'EX', claim_ttl)
    redis.call('SET', lock2_key, '1', 'EX', claim_ttl)
    return 1
end
-- Rollback: re-add whichever was removed
if r1 == 1 then redis.call('ZADD', queue_key, elo1, member1) end
if r2 == 1 then redis.call('ZADD', queue_key, elo2, member2) end
return 0
"""

# Atomically join queue: check active match / claim, clean ghosts, acquire lock, enqueue.
# Returns: 1 = success, 0 = already in match/claim, -1 = already in queue (lock held + member present)
ATOMIC_JOIN_QUEUE = """
local uid = ARGV[1]
local elo = tonumber(ARGV[2])
local member = ARGV[3]
local active_match_key = KEYS[1]
local lock_key = KEYS[2]
local queue_key = KEYS[3]
local member_key = KEYS[4]
local claim_key = KEYS[5]

-- Check if already in active match or pairing claim
if redis.call('EXISTS', active_match_key) == 1 then
    return 0
end
if redis.call('EXISTS', claim_key) == 1 then
    return 0
end

-- If already queued (lock + valid member), refresh lock TTL and return idempotent success
local existing = redis.call('GET', member_key)
if existing and redis.call('ZSCORE', queue_key, existing) then
    redis.call('SET', lock_key, '1', 'EX', 60)
    return -1
end

-- Ghost cleanup: remove any queue members for this uid (stale locks / expired locks)
if existing then
    redis.call('ZREM', queue_key, existing)
end
local all = redis.call('ZRANGE', queue_key, 0, -1)
local prefix = uid .. ':'
for i, m in ipairs(all) do
    local ms = tostring(m)
    if string.sub(ms, 1, string.len(prefix)) == prefix then
        redis.call('ZREM', queue_key, ms)
    end
end

-- Acquire / refresh lock and enqueue
redis.call('SET', lock_key, '1', 'EX', 60)
redis.call('ZADD', queue_key, elo, member)
redis.call('SET', member_key, member, 'EX', 3600)
return 1
"""

# Atomically leave queue: remove exact member via lookup key, release lock.
# Does NOT clear pairing claim — leave during claim is a no-op for rejoin purposes.
# Returns: 1 = success, 0 = not found, -1 = blocked by pairing claim
ATOMIC_LEAVE_QUEUE = """
local queue_key = KEYS[1]
local lock_key = KEYS[2]
local member_key = KEYS[3]
local claim_key = KEYS[4]
local uid = ARGV[1]

if redis.call('EXISTS', claim_key) == 1 then
    -- Still being paired — refuse leave so they can't rejoin as a ghost
    return -1
end

local member = redis.call('GET', member_key)
local removed = 0
if member then
    redis.call('ZREM', queue_key, member)
    redis.call('DEL', member_key)
    removed = 1
else
    -- Legacy fallback: only used for entries without a member key
    local members = redis.call('ZRANGE', queue_key, 0, -1)
    for i, m in ipairs(members) do
        local member_str = tostring(m)
        if string.sub(member_str, 1, string.len(uid)) == uid then
            redis.call('ZREM', queue_key, member_str)
            removed = 1
            break
        end
    end
end

-- Always release lock (idempotent)
redis.call('DEL', lock_key)
return removed
"""

# Atomically claim a solo player for bot fallback (ZREM + claim key).
# Returns 1 on success, 0 if member already gone.
ATOMIC_BOT_CLAIM = """
local queue_key = KEYS[1]
local claim_key = KEYS[2]
local member_key = KEYS[3]
local lock_key = KEYS[4]
local member = ARGV[1]
local claim_ttl = tonumber(ARGV[2])

local removed = redis.call('ZREM', queue_key, member)
if removed ~= 1 then
    return 0
end
redis.call('SET', claim_key, '1', 'EX', claim_ttl)
redis.call('DEL', member_key)
-- Keep lock until active_match is set (prevents rejoin during create)
redis.call('SET', lock_key, '1', 'EX', claim_ttl)
return 1
"""


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Public API
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def join_queue(redis: Redis, user_id: uuid.UUID, elo: int) -> bool:
    """
    Add a player to the matchmaking queue.

    PRODUCTION: Uses atomic Lua script to prevent race conditions.
    All checks (active match, claim, lock, enqueue) happen atomically.
    Ghost queue members for the same uid are always cleaned on join.

    Guards:
      1. Rejects if the user is already in an active match or pairing claim
      2. Idempotent if already queued (refreshes lock TTL)
      3. Atomically cleans ghosts and adds to queue

    Redis structure:
      Sorted Set "matchmaking:queue"
        member = "<user_id>:<join_timestamp>"
        score  = ELO rating
    """
    uid = str(user_id)
    member = f"{uid}:{time.time()}"

    async def _is_in_queue() -> bool:
        """O(1) check whether the user already has a member entry in the queue."""
        existing = await redis.get(RedisKey.matchmaking_member(uid))
        if not existing:
            return False
        member_str = existing.decode() if isinstance(existing, bytes) else existing
        score = await redis.zscore(RedisKey.MATCHMAKING_QUEUE, member_str)
        return score is not None

    async def _attempt_join() -> int:
        return await redis.eval(
            ATOMIC_JOIN_QUEUE,
            5,  # number of KEYS
            RedisKey.user_active_match(uid),      # KEYS[1]
            RedisKey.matchmaking_lock(uid),       # KEYS[2]
            RedisKey.MATCHMAKING_QUEUE,           # KEYS[3]
            RedisKey.matchmaking_member(uid),     # KEYS[4]
            RedisKey.matchmaking_claim(uid),      # KEYS[5]
            uid,                                  # ARGV[1]
            str(elo),                             # ARGV[2]
            member,                               # ARGV[3]
        )

    result = await _attempt_join()

    if result == 0:
        raise AlreadyInMatch()

    if result == 1:
        logger.info(f"[MATCHMAKING] Player {uid} queued (ELO={elo})")
        return True

    if result == -1:
        # Idempotent: already in queue (lock refreshed by Lua)
        logger.info(f"[MATCHMAKING] Player {uid} already queued (idempotent join)")
        return True

    logger.error(f"[MATCHMAKING] Unexpected join_queue result: {result} (uid={uid})", exc_info=True)
    return True


async def leave_queue(redis: Redis, user_id: uuid.UUID) -> bool:
    """
    Remove a player from the matchmaking queue and release their lock.
    
    PRODUCTION: Uses atomic Lua script to prevent race conditions.
    Leave during an active pairing claim is blocked (returns True idempotently
    without clearing the claim — prevents leave/rejoin double-pair races).
    """
    uid = str(user_id)

    result = await redis.eval(
        ATOMIC_LEAVE_QUEUE,
        4,  # number of KEYS
        RedisKey.MATCHMAKING_QUEUE,           # KEYS[1]
        RedisKey.matchmaking_lock(uid),       # KEYS[2]
        RedisKey.matchmaking_member(uid),     # KEYS[3]
        RedisKey.matchmaking_claim(uid),      # KEYS[4]
        uid,                                  # ARGV[1]
    )

    if result == -1:
        logger.info(f"[MATCHMAKING] Player {uid} leave blocked (pairing claim held)")
        return True

    if result == 0:
        logger.info(f"[MATCHMAKING] Player {uid} not in queue (idempotent leave)")
        return True

    logger.info(f"[MATCHMAKING] Player {uid} left queue")
    return True


async def get_queue_position(redis: Redis, user_id: uuid.UUID) -> Optional[dict]:
    """
    Get a player's queue status: position, wait time, current ELO window.
    Returns None if not in queue.

    Uses the per-user member key for O(log N) lookups instead of scanning the queue.
    """
    uid = str(user_id)
    member = await redis.get(RedisKey.matchmaking_member(uid))
    if not member:
        return None

    member_str = member.decode() if isinstance(member, bytes) else member
    rank = await redis.zrank(RedisKey.MATCHMAKING_QUEUE, member_str)
    if rank is None:
        return None

    score = await redis.zscore(RedisKey.MATCHMAKING_QUEUE, member_str)
    total = await redis.zcard(RedisKey.MATCHMAKING_QUEUE)
    join_ts = float(member_str.split(":")[1])
    wait_secs = time.time() - join_ts
    return {
        "position": int(rank) + 1,
        "total_in_queue": int(total),
        "wait_seconds": round(wait_secs, 1),
        "current_elo_window": _calculate_elo_window(wait_secs),
        "elo": int(score) if score is not None else 0,
    }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Matchmaker — called periodically by the matchmaking worker
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def process_queue(redis: Redis, db: AsyncSession) -> list[uuid.UUID]:
    """
    Core matchmaking loop.

    Multi-instance safety:
      1. SETNX global lock with extended TTL → only ONE pod processes at a time
      2. Lua ATOMIC_PAIR_CLAIM → ZREM both + set claims atomically
         (if another pod snuck in, the Lua script rolls back and returns 0)
      3. Pairing claim keys hold exclusive ownership until active_match is set

    Algorithm:
      - Pull all queued players from the sorted set
      - Sort by wait time (longest first → fairness)
      - For each unmatched player, find the closest-ELO candidate
        within their expanding window
      - If found, atomically remove both via Lua and create a match

    Returns list of newly created match IDs.
    """
    # Global lock TTL must cover _create_match (DB + Redis). Refresh while holding.
    GLOBAL_LOCK_TTL = 15
    if not await redis.set(RedisKey.MATCHMAKING_GLOBAL_LOCK, "1", nx=True, ex=GLOBAL_LOCK_TTL):
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

            # Refresh global lock so long DB writes don't expire mid-cycle
            await redis.expire(RedisKey.MATCHMAKING_GLOBAL_LOCK, GLOBAL_LOCK_TTL)

            # ── Atomic ZREM + claim (Lua) ─────────────────
            claim_ttl = 30
            ok = await redis.eval(
                ATOMIC_PAIR_CLAIM,
                7,
                RedisKey.MATCHMAKING_QUEUE,
                RedisKey.matchmaking_claim(player["user_id"]),
                RedisKey.matchmaking_claim(best["user_id"]),
                RedisKey.matchmaking_member(player["user_id"]),
                RedisKey.matchmaking_member(best["user_id"]),
                RedisKey.matchmaking_lock(player["user_id"]),
                RedisKey.matchmaking_lock(best["user_id"]),
                player["member"],
                best["member"],
                str(player["elo"]),
                str(best["elo"]),
                str(claim_ttl),
            )

            if not ok:
                # Another instance removed one of them — skip, retry next cycle
                logger.debug(
                    f"[MATCHMAKING] Atomic claim failed for "
                    f"{player['user_id']} vs {best['user_id']} — retrying"
                )
                continue

            # ── Create match ─────────────────────────────
            try:
                match_id = await _create_match(
                    db, redis,
                    player["user_id"], player["elo"],
                    best["user_id"], best["elo"],
                )
            except Exception as create_err:
                logger.error(
                    f"[MATCHMAKING] _create_match failed for "
                    f"{player['user_id']} vs {best['user_id']}: {create_err}",
                    exc_info=True,
                )
                # Requeue both players and release claims
                await _requeue_player(redis, player)
                await _requeue_player(redis, best)
                await redis.delete(
                    RedisKey.matchmaking_claim(player["user_id"]),
                    RedisKey.matchmaking_claim(best["user_id"]),
                )
                continue

            matched_user_ids.add(player["user_id"])
            matched_user_ids.add(best["user_id"])
            created_matches.append(match_id)

            # Release per-user locks, claims, and member lookup keys
            # (active_match now blocks rejoin)
            await redis.delete(
                RedisKey.matchmaking_lock(player["user_id"]),
                RedisKey.matchmaking_lock(best["user_id"]),
                RedisKey.matchmaking_claim(player["user_id"]),
                RedisKey.matchmaking_claim(best["user_id"]),
                RedisKey.matchmaking_member(player["user_id"]),
                RedisKey.matchmaking_member(best["user_id"]),
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


async def _requeue_player(redis: Redis, player: dict) -> None:
    """Restore a player to the queue after a failed match create."""
    uid = player["user_id"]
    member = f"{uid}:{time.time()}"
    await redis.zadd(RedisKey.MATCHMAKING_QUEUE, {member: player["elo"]})
    await redis.set(RedisKey.matchmaking_member(uid), member, ex=3600)
    await redis.set(RedisKey.matchmaking_lock(uid), "1", ex=60)
    logger.info(f"[MATCHMAKING] Requeued {uid} after create failure")


async def _try_bot_fallback_match(db: AsyncSession, redis: Redis, player: dict) -> uuid.UUID | None:
    """Pair a long-waiting solo player with a bot using atomic claim."""
    from backend.services.bot_service import get_random_bot_for_elo

    bot = await get_random_bot_for_elo(db, player["elo"], player["user_id"])
    if bot is None:
        return None

    claim_ttl = 30
    ok = await redis.eval(
        ATOMIC_BOT_CLAIM,
        4,
        RedisKey.MATCHMAKING_QUEUE,
        RedisKey.matchmaking_claim(player["user_id"]),
        RedisKey.matchmaking_member(player["user_id"]),
        RedisKey.matchmaking_lock(player["user_id"]),
        player["member"],
        str(claim_ttl),
    )
    if not ok:
        logger.debug(f"[MATCHMAKING] Bot claim failed for {player['user_id']} (already claimed)")
        return None

    bot_id = str(bot.id)
    try:
        match_id = await _create_match(
            db, redis,
            player["user_id"], player["elo"],
            bot_id, bot.elo,
        )
    except Exception as create_err:
        logger.error(
            f"[MATCHMAKING] Bot match create failed for {player['user_id']}: {create_err}",
            exc_info=True,
        )
        await _requeue_player(redis, player)
        await redis.delete(RedisKey.matchmaking_claim(player["user_id"]))
        return None

    await redis.delete(
        RedisKey.matchmaking_lock(player["user_id"]),
        RedisKey.matchmaking_claim(player["user_id"]),
        RedisKey.matchmaking_member(player["user_id"]),
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
        member = await redis.get(RedisKey.matchmaking_member(str(user_id)))
        if member:
            member_str = member.decode() if isinstance(member, bytes) else str(member)
            await redis.zrem(RedisKey.MATCHMAKING_QUEUE, member_str)
            await redis.delete(RedisKey.matchmaking_member(str(user_id)))
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
    # Select ELO-appropriate problems (3 for multi-problem battles)
    from backend.services import match_service as match_svc

    avg_elo = (p1_elo + p2_elo) // 2
    problems = await problem_service.get_problems_for_match(
        db, avg_elo, count=match_svc.MATCH_PROBLEM_COUNT
    )
    primary = problems[0]

    # ── PostgreSQL: persist match (in transaction) ────────
    match = Match(
        player1_id=uuid.UUID(p1_id),
        player2_id=uuid.UUID(p2_id),
        problem_id=primary.id,
        status=MatchStatus.ACTIVE,
        player1_elo_before=p1_elo,
        player2_elo_before=p2_elo,
        duration_seconds=settings.match_duration_seconds,
    )
    db.add(match)
    await db.flush()
    await match_svc.attach_match_problems(db, match, problems)

    try:
        await db.commit()
        await db.refresh(match)
    except Exception as e:
        await db.rollback()
        logger.error(f"[MATCHMAKING] Failed to create match in DB: {e}")
        raise

    mid = str(match.id)
    ttl = settings.match_duration_seconds + 60  # Buffer for cleanup

    # ── Redis: set up state. If this fails, cancel the DB match so join
    # cannot create a second ACTIVE while players think they are free.
    try:
        expiry_ts = time.time() + settings.match_duration_seconds
        problem_ids_csv = ",".join(str(p.id) for p in problems)

        pipe = redis.pipeline()
        pipe.set(RedisKey.match_timer(mid), str(expiry_ts), ex=ttl)
        pipe.hset(RedisKey.match_state(mid), mapping={
            "status": MatchStatus.ACTIVE,
            "player1_id": p1_id,
            "player2_id": p2_id,
            "problem_id": str(primary.id),
            "problem_ids": problem_ids_csv,
            "problem_title": primary.title,
            "started_at": str(time.time()),
        })
        pipe.expire(RedisKey.match_state(mid), ttl)
        pipe.set(RedisKey.user_active_match(p1_id), mid, ex=ttl)
        pipe.set(RedisKey.user_active_match(p2_id), mid, ex=ttl)
        await pipe.execute()
    except Exception as e:
        logger.error(
            f"[MATCHMAKING] Failed to set Redis state for match {mid}: {e}",
            exc_info=True,
        )
        try:
            match.status = MatchStatus.CANCELLED
            match.ended_at = datetime.now(timezone.utc)
            await db.commit()
        except Exception as cancel_err:
            await db.rollback()
            logger.error(
                f"[MATCHMAKING] Failed to cancel match {mid} after Redis error: {cancel_err}",
                exc_info=True,
            )
        try:
            await redis.delete(
                RedisKey.match_timer(mid),
                RedisKey.match_state(mid),
                RedisKey.user_active_match(p1_id),
                RedisKey.user_active_match(p2_id),
            )
        except Exception:
            pass
        raise RuntimeError(f"Redis state setup failed for match {mid}") from e

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
