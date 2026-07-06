"""
Match service — match lifecycle management, timer control, state transitions.
"""

import time
import uuid
import logging
from datetime import datetime, timezone

from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from typing import Optional

from backend.config import settings
from backend.core.constants import MatchStatus, SubmissionStatus, RedisKey
from backend.core.exceptions import MatchNotFound, MatchNotActive, MatchExpired, NotMatchParticipant
from backend.models.match import Match
from backend.models.submission import Submission
from backend.services import rating_service

logger = logging.getLogger(__name__)


async def get_match(db: AsyncSession, match_id: uuid.UUID) -> Match:
    """Get match with relationships loaded."""
    result = await db.execute(
        select(Match)
        .where(Match.id == match_id)
        .options(
            selectinload(Match.player1),
            selectinload(Match.player2),
            selectinload(Match.problem),
            selectinload(Match.winner),
        )
    )
    match = result.scalar_one_or_none()
    if not match:
        raise MatchNotFound()
    return match


async def get_match_history(
    db: AsyncSession, user_id: uuid.UUID, limit: int = 20, offset: int = 0
) -> list[Match]:
    """Get match history for a user."""
    result = await db.execute(
        select(Match)
        .where(
            ((Match.player1_id == user_id) | (Match.player2_id == user_id))
            & (Match.status == MatchStatus.COMPLETED)
        )
        .order_by(Match.started_at.desc())
        .offset(offset)
        .limit(limit)
        .options(
            selectinload(Match.player1),
            selectinload(Match.player2),
        )
    )
    return list(result.scalars().all())


async def validate_match_active(
    redis: Optional[Redis], match_id: uuid.UUID, user_id: uuid.UUID,
    db: Optional["AsyncSession"] = None,
) -> None:
    """Validate that a match is active and the user is a participant."""
    if redis is None:
        # Dev mode: fall back to DB validation
        if db is None:
            return
        match = await get_match(db, match_id)
        if match.status != MatchStatus.ACTIVE:
            raise MatchNotActive()
        user_id_str = str(user_id)
        if user_id_str != str(match.player1_id) and user_id_str != str(match.player2_id):
            raise NotMatchParticipant()
        return

    match_id_str = str(match_id)

    state = await redis.hgetall(RedisKey.match_state(match_id_str))
    if not state:
        raise MatchNotFound()

    status = state.get(b"status", b"").decode()
    if status != MatchStatus.ACTIVE:
        raise MatchNotActive()

    p1 = state.get(b"player1_id", b"").decode()
    p2 = state.get(b"player2_id", b"").decode()
    user_id_str = str(user_id)
    if user_id_str != p1 and user_id_str != p2:
        raise NotMatchParticipant()

    # Check timer
    timer_val = await redis.get(RedisKey.match_timer(match_id_str))
    if timer_val:
        expiry = float(timer_val)
        if time.time() > expiry:
            raise MatchExpired()


async def get_remaining_time(redis: Optional[Redis], match_id: uuid.UUID) -> Optional[int]:
    """Get remaining seconds for an active match."""
    if redis is None:
        return None
    timer_val = await redis.get(RedisKey.match_timer(str(match_id)))
    if not timer_val:
        return None
    expiry = float(timer_val)
    remaining = int(expiry - time.time())
    return max(0, remaining)


async def complete_match(
    db: AsyncSession,
    redis: Optional[Redis],
    match_id: uuid.UUID,
    reason: str = "timeout",
) -> dict:
    """
    Complete a match: determine winner, update ELO, clean up Redis state.

    PRODUCTION: Idempotent - safe to call multiple times.
    Uses a Redis distributed lock to prevent race conditions between
    the timeout handler and judge worker completing the same match.
    Returns empty dict if match is already completed.

    Returns match result dict for WebSocket broadcast.
    """
    lock_key = f"lock:match_complete:{match_id}"
    if redis is not None:
        acquired = await redis.set(lock_key, "1", nx=True, ex=10)
        if not acquired:
            logger.debug(f"Match {match_id} completion already in progress (lock held)")
            return {}

    try:
        match = await get_match(db, match_id)
        if match.status != MatchStatus.ACTIVE:
            logger.debug(f"Match {match_id} already completed (status={match.status})")
            return {}

        # Determine winner from submissions
        winner_id = await _determine_winner(db, match)

        # Skip ELO update on timeout draw (neither player solved it)
        if reason == "timeout" and winner_id is None:
            p1_new = match.player1.elo
            p2_new = match.player2.elo
            p1_delta = 0
            p2_delta = 0
        else:
            # Update ELO ratings
            p1_new, p2_new, p1_delta, p2_delta = await rating_service.update_ratings(
                db, match.player1_id, match.player2_id, winner_id
            )

        # Update match record (atomic transaction)
        try:
            match.status = MatchStatus.COMPLETED
            match.winner_id = winner_id
            match.ended_at = datetime.now(timezone.utc)
            match.player1_elo_after = p1_new
            match.player2_elo_after = p2_new

            await db.commit()
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to complete match {match_id}: {e}")
            raise

        # Clean up Redis (skip if Redis disabled)
        if redis is not None:
            match_id_str = str(match_id)
            await redis.delete(
                RedisKey.match_state(match_id_str),
                RedisKey.match_timer(match_id_str),
                RedisKey.user_active_match(str(match.player1_id)),
                RedisKey.user_active_match(str(match.player2_id)),
            )

        # Always clean up dev-mode active match tracking
        try:
            from backend.services.matchmaking_memory import memory_queue
            await memory_queue.clear_match_for_both(str(match.player1_id), str(match.player2_id))
        except Exception:
            pass

        # Resolve usernames for frontend display
        winner_username = None
        loser_username = None
        if winner_id:
            if winner_id == match.player1_id:
                winner_username = match.player1.username
                loser_username = match.player2.username
            else:
                winner_username = match.player2.username
                loser_username = match.player1.username

        logger.info(f"Match {match_id} completed. Winner: {winner_id}. Reason: {reason}")

        result = {
            "match_id": str(match_id),
            "winner_id": str(winner_id) if winner_id else None,
            "winner_username": winner_username,
            "loser_username": loser_username,
            "reason": reason,
            "player1_id": str(match.player1_id),
            "player2_id": str(match.player2_id),
            "player1_elo_delta": p1_delta,
            "player2_elo_delta": p2_delta,
            "player1_new_elo": p1_new,
            "player2_new_elo": p2_new,
            "problem_title": match.problem.title if match.problem else None,
        }
        await _record_event_wins(redis, match, winner_id)
        return result
    finally:
        if redis is not None:
            await redis.delete(lock_key)


async def complete_match_with_winner(
    db: AsyncSession,
    redis: Optional[Redis],
    match_id: uuid.UUID,
    winner_id: uuid.UUID,
    reason: str = "accepted",
) -> dict:
    """
    Complete a match with a specific winner (used when a submission is ACCEPTED).

    Unlike complete_match(), this does NOT re-query the DB for accepted submissions.
    The caller already knows the winner — they are the submitter whose solution was accepted.

    PRODUCTION: Idempotent - returns {} if match is already completed.
    Uses a Redis distributed lock to prevent race conditions.
    Uses the same result_data shape as complete_match().
    """
    lock_key = f"lock:match_complete:{match_id}"
    if redis is not None:
        acquired = await redis.set(lock_key, "1", nx=True, ex=10)
        if not acquired:
            logger.debug(f"Match {match_id} completion already in progress (lock held)")
            return {}

    try:
        match = await get_match(db, match_id)
        if match.status != MatchStatus.ACTIVE:
            logger.debug(f"Match {match_id} already completed (status={match.status})")
            return {}

        # Update ELO ratings
        p1_new, p2_new, p1_delta, p2_delta = await rating_service.update_ratings(
            db, match.player1_id, match.player2_id, winner_id
        )

        # Update match record (atomic transaction)
        try:
            match.status = MatchStatus.COMPLETED
            match.winner_id = winner_id
            match.ended_at = datetime.now(timezone.utc)
            match.player1_elo_after = p1_new
            match.player2_elo_after = p2_new

            await db.commit()
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to complete match {match_id}: {e}")
            raise

        # Clean up Redis (skip if Redis disabled)
        if redis is not None:
            match_id_str = str(match_id)
            await redis.delete(
                RedisKey.match_state(match_id_str),
                RedisKey.match_timer(match_id_str),
                RedisKey.user_active_match(str(match.player1_id)),
                RedisKey.user_active_match(str(match.player2_id)),
            )

        # Always clean up dev-mode active match tracking
        try:
            from backend.services.matchmaking_memory import memory_queue
            await memory_queue.clear_match_for_both(str(match.player1_id), str(match.player2_id))
        except Exception:
            pass

        # Resolve usernames for frontend display
        winner_username = None
        loser_username = None
        if winner_id == match.player1_id:
            winner_username = match.player1.username
            loser_username = match.player2.username
        else:
            winner_username = match.player2.username
            loser_username = match.player1.username

        logger.info(
            f"Match {match_id} completed. "
            f"Winner: {winner_id} ({winner_username}). Reason: {reason}"
        )

        result = {
            "match_id": str(match_id),
            "winner_id": str(winner_id),
            "winner_username": winner_username,
            "loser_username": loser_username,
            "reason": reason,
            "player1_id": str(match.player1_id),
            "player2_id": str(match.player2_id),
            "player1_elo_delta": p1_delta,
            "player2_elo_delta": p2_delta,
            "player1_new_elo": p1_new,
            "player2_new_elo": p2_new,
            "problem_title": match.problem.title if match.problem else None,
        }
        await _record_event_wins(redis, match, winner_id)
        return result
    finally:
        if redis is not None:
            await redis.delete(lock_key)


async def forfeit_match(
    db: AsyncSession,
    redis: Optional[Redis],
    match_id: uuid.UUID,
    forfeiter_id: uuid.UUID,
) -> dict:
    """
    Forfeit an active match on behalf of one player.

    Rules:
      - Only participants can forfeit
      - Match must be ACTIVE; otherwise returns empty dict (idempotent)
      - Opponent is declared winner
      - ELO ratings are updated via rating_service
      - Redis state (match_state, match_timer, user_active_match) is cleaned up

    Returns:
      Same result_data shape as complete_match(), or {} if already completed.
    """
    lock_key = f"lock:match_complete:{match_id}"
    if redis is not None:
        acquired = await redis.set(lock_key, "1", nx=True, ex=10)
        if not acquired:
            logger.debug(f"Match {match_id} forfeit blocked by lock")
            return {}

    try:
        match = await get_match(db, match_id)

        if match.status != MatchStatus.ACTIVE:
            logger.debug(f"Match {match_id} already completed (status={match.status})")
            return {}

        # Verify forfeiter is a participant and determine winner
        if forfeiter_id == match.player1_id:
            winner_id = match.player2_id
        elif forfeiter_id == match.player2_id:
            winner_id = match.player1_id
        else:
            raise NotMatchParticipant()

        # Update ELO ratings
        p1_new, p2_new, p1_delta, p2_delta = await rating_service.update_ratings(
            db, match.player1_id, match.player2_id, winner_id
        )

        # Persist match completion
        try:
            match.status = MatchStatus.COMPLETED
            match.winner_id = winner_id
            match.ended_at = datetime.now(timezone.utc)
            match.player1_elo_after = p1_new
            match.player2_elo_after = p2_new

            await db.commit()
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to forfeit match {match_id}: {e}")
            raise

        # Clean up Redis (skip if Redis disabled)
        if redis is not None:
            match_id_str = str(match_id)
            await redis.delete(
                RedisKey.match_state(match_id_str),
                RedisKey.match_timer(match_id_str),
                RedisKey.user_active_match(str(match.player1_id)),
                RedisKey.user_active_match(str(match.player2_id)),
            )

        # Always clean up dev-mode active match tracking
        try:
            from backend.services.matchmaking_memory import memory_queue
            await memory_queue.clear_match_for_both(str(match.player1_id), str(match.player2_id))
        except Exception:
            pass

        logger.info(f"Match {match_id} forfeited by {forfeiter_id}. Winner: {winner_id}")

        # Resolve usernames for frontend display
        if winner_id == match.player1_id:
            winner_username = match.player1.username
            loser_username = match.player2.username
        else:
            winner_username = match.player2.username
            loser_username = match.player1.username

        return {
            "match_id": str(match_id),
            "winner_id": str(winner_id) if winner_id else None,
            "winner_username": winner_username,
            "loser_username": loser_username,
            "reason": "forfeit",
            "player1_id": str(match.player1_id),
            "player2_id": str(match.player2_id),
            "player1_elo_delta": p1_delta,
            "player2_elo_delta": p2_delta,
            "player1_new_elo": p1_new,
            "player2_new_elo": p2_new,
        }
    finally:
        if redis is not None:
            await redis.delete(lock_key)


async def check_and_complete_expired_matches(
    db: AsyncSession, redis: Redis
) -> list[uuid.UUID]:
    """
    Scan for expired active matches and complete them.
    Called periodically by the matchmaking worker.
    """
    result = await db.execute(
        select(Match).where(Match.status == MatchStatus.ACTIVE)
    )
    matches = result.scalars().all()
    completed = []

    for match in matches:
        remaining = await get_remaining_time(redis, match.id)
        if remaining is not None and remaining <= 0:
            await complete_match(db, redis, match.id, reason="timeout")
            completed.append(match.id)

    return completed


async def _determine_winner(db: AsyncSession, match: Match) -> Optional[uuid.UUID]:
    """
    Determine winner based on submissions.

    Rules:
    1. Player with accepted submission wins
    2. If both accepted → first to submit accepted wins
    3. If neither accepted → draw (None)
    """
    result = await db.execute(
        select(Submission)
        .where(
            (Submission.match_id == match.id)
            & (Submission.status == SubmissionStatus.ACCEPTED)
        )
        .order_by(Submission.judged_at.asc())
    )
    accepted_submissions = result.scalars().all()

    if not accepted_submissions:
        return None  # Draw

    # First accepted submission wins
    return accepted_submissions[0].user_id


async def _record_event_wins(
    redis: Optional[Redis],
    match: Match,
    winner_id: Optional[uuid.UUID],
) -> None:
    if not winner_id:
        return
    winner = match.player1 if match.player1_id == winner_id else match.player2
    if winner and winner.is_bot:
        return
    try:
        from backend.services import event_service

        for event in event_service.get_active_events():
            if event.event_type == "cup":
                await event_service.record_event_win(
                    redis,
                    event_id=event.id,
                    user_id=str(winner_id),
                )
    except Exception as exc:
        logger.warning("Failed to record event win: %s", exc)


async def get_match_recap(db: AsyncSession, match_id: uuid.UUID) -> Optional[dict]:
    """Public-safe match summary for share links."""
    match = await get_match(db, match_id)
    if match.status != MatchStatus.COMPLETED:
        return None
    return {
        "match_id": str(match.id),
        "problem_title": match.problem.title if match.problem else "Unknown",
        "player1_username": match.player1.username,
        "player2_username": match.player2.username,
        "winner_username": match.winner.username if match.winner else None,
        "reason": "completed",
        "started_at": match.started_at.isoformat() if match.started_at else None,
        "ended_at": match.ended_at.isoformat() if match.ended_at else None,
        "player1_elo_delta": (match.player1_elo_after or 0) - match.player1_elo_before,
        "player2_elo_delta": (match.player2_elo_after or 0) - match.player2_elo_before,
    }
