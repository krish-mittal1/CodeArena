"""
Match service — match lifecycle management, timer control, state transitions.
"""

import time
import uuid
import logging
from datetime import datetime, timezone

from redis.asyncio import Redis
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from typing import Optional

from backend.config import settings
from backend.core.constants import MatchStatus, SubmissionStatus, RedisKey
from backend.core.exceptions import MatchNotFound, MatchNotActive, MatchExpired, NotMatchParticipant
from backend.models.match import Match
from backend.models.match_problem import MatchProblem
from backend.models.problem import Problem
from backend.models.submission import Submission
from backend.services import rating_service

logger = logging.getLogger(__name__)

MATCH_PROBLEM_COUNT = 3


def _match_load_options(*, include_problems: bool = True):
    opts = [
        selectinload(Match.player1),
        selectinload(Match.player2),
        selectinload(Match.problem),
        selectinload(Match.winner),
    ]
    if include_problems:
        opts.append(
            selectinload(Match.match_problems).selectinload(MatchProblem.problem)
        )
    return opts


def get_ordered_match_problems(match: Match) -> list[Problem]:
    """
    Return ordered problems for a match.
    Prefer match_problems rows; fall back to legacy match.problem_id.
    """
    rows = getattr(match, "match_problems", None) or []
    if rows:
        return [mp.problem for mp in sorted(rows, key=lambda r: r.order_index) if mp.problem]

    if match.problem:
        return [match.problem]
    return []


def get_match_problem_ids(match: Match) -> list[uuid.UUID]:
    problems = get_ordered_match_problems(match)
    if problems:
        return [p.id for p in problems]
    return [match.problem_id] if match.problem_id else []


def match_problem_summaries(match: Match) -> list[dict]:
    """Lightweight problem list for WS / API payloads."""
    problems = get_ordered_match_problems(match)
    if not problems and match.problem_id:
        return [{
            "id": str(match.problem_id),
            "title": match.problem.title if match.problem else "",
            "difficulty": getattr(match.problem, "difficulty", None),
            "order_index": 0,
        }]
    return [
        {
            "id": str(p.id),
            "title": p.title,
            "difficulty": p.difficulty,
            "order_index": i,
        }
        for i, p in enumerate(problems)
    ]


def build_match_found_payload(match: Match) -> dict:
    """Canonical match_found / hydrate payload including problems[]."""
    problems = match_problem_summaries(match)
    primary = problems[0] if problems else {
        "id": str(match.problem_id),
        "title": match.problem.title if match.problem else "",
    }
    return {
        "match_id": str(match.id),
        "problem_id": primary["id"],
        "problem_title": primary.get("title") or "",
        "problems": problems,
        "duration_seconds": match.duration_seconds,
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
    }


async def attach_match_problems(
    db: AsyncSession,
    match: Match,
    problems: list[Problem],
) -> None:
    """Persist ordered match ↔ problem rows (caller commits)."""
    for i, problem in enumerate(problems):
        db.add(
            MatchProblem(
                match_id=match.id,
                problem_id=problem.id,
                order_index=i,
            )
        )
    await db.flush()


async def user_has_accepted_all_match_problems(
    db: AsyncSession,
    match: Match,
    user_id: uuid.UUID,
) -> bool:
    """True if user has at least one ACCEPTED submission for every match problem."""
    problem_ids = get_match_problem_ids(match)
    if not problem_ids:
        return False

    result = await db.execute(
        select(Submission.problem_id)
        .where(
            Submission.match_id == match.id,
            Submission.user_id == user_id,
            Submission.status == SubmissionStatus.ACCEPTED,
            Submission.problem_id.in_(problem_ids),
        )
        .distinct()
    )
    accepted = {row[0] for row in result.all()}
    return all(pid in accepted for pid in problem_ids)


async def count_user_accepted_match_problems(
    db: AsyncSession,
    match: Match,
    user_id: uuid.UUID,
) -> int:
    problem_ids = get_match_problem_ids(match)
    if not problem_ids:
        return 0
    result = await db.execute(
        select(func.count(func.distinct(Submission.problem_id))).where(
            Submission.match_id == match.id,
            Submission.user_id == user_id,
            Submission.status == SubmissionStatus.ACCEPTED,
            Submission.problem_id.in_(problem_ids),
        )
    )
    return int(result.scalar_one() or 0)


async def _lock_active_match_for_completion(
    db: AsyncSession, match_id: uuid.UUID
) -> Optional[Match]:
    """
    SELECT … FOR UPDATE the match row. Returns the match only if still ACTIVE.

    This is the durable idempotency gate for ELO: Redis lock TTL expiry or
    dual workers cannot both pass this and call update_ratings.
    """
    result = await db.execute(
        select(Match)
        .where(Match.id == match_id)
        .options(*_match_load_options())
        .with_for_update()
    )
    match = result.scalar_one_or_none()
    if not match:
        raise MatchNotFound()
    if match.status != MatchStatus.ACTIVE:
        logger.debug(
            f"Match {match_id} already completed (status={match.status})"
        )
        return None
    return match


async def get_match(db: AsyncSession, match_id: uuid.UUID) -> Match:
    """Get match with relationships loaded."""
    result = await db.execute(
        select(Match)
        .where(Match.id == match_id)
        .options(*_match_load_options())
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


async def _validate_match_active_from_db(
    db: AsyncSession, match_id: uuid.UUID, user_id: uuid.UUID,
) -> None:
    """DB fallback when Redis match_state is missing (same idea as started_at timer)."""
    match = await get_match(db, match_id)
    if match.status != MatchStatus.ACTIVE:
        raise MatchNotActive()
    user_id_str = str(user_id)
    if user_id_str != str(match.player1_id) and user_id_str != str(match.player2_id):
        raise NotMatchParticipant()
    if match.started_at:
        started_at = match.started_at
        if started_at.tzinfo is None:
            started_at = started_at.replace(tzinfo=timezone.utc)
        elapsed = (datetime.now(timezone.utc) - started_at).total_seconds()
        if elapsed >= match.duration_seconds:
            raise MatchExpired()


async def validate_match_active(
    redis: Optional[Redis], match_id: uuid.UUID, user_id: uuid.UUID,
    db: Optional["AsyncSession"] = None,
) -> None:
    """Validate that a match is active and the user is a participant."""
    if redis is None:
        # Dev mode: fall back to DB validation
        if db is None:
            return
        await _validate_match_active_from_db(db, match_id, user_id)
        return

    match_id_str = str(match_id)

    state = await redis.hgetall(RedisKey.match_state(match_id_str))
    if not state:
        # Redis miss: allow submit if DB still shows ACTIVE for this player
        if db is None:
            raise MatchNotFound()
        logger.warning(
            "[MATCH] Redis match_state missing for %s — validating via DB",
            match_id_str,
        )
        await _validate_match_active_from_db(db, match_id, user_id)
        return

    status = state.get(b"status", b"").decode()
    if status != MatchStatus.ACTIVE:
        raise MatchNotActive()

    p1 = state.get(b"player1_id", b"").decode()
    p2 = state.get(b"player2_id", b"").decode()
    user_id_str = str(user_id)
    if user_id_str != p1 and user_id_str != p2:
        raise NotMatchParticipant()

    # Check timer (Redis) with DB started_at fallback
    timer_val = await redis.get(RedisKey.match_timer(match_id_str))
    if timer_val:
        expiry = float(timer_val)
        if time.time() > expiry:
            raise MatchExpired()
    elif db is not None:
        match = await get_match(db, match_id)
        if match.started_at:
            started_at = match.started_at
            if started_at.tzinfo is None:
                started_at = started_at.replace(tzinfo=timezone.utc)
            elapsed = (datetime.now(timezone.utc) - started_at).total_seconds()
            if elapsed >= match.duration_seconds:
                raise MatchExpired()


async def get_remaining_time(
    redis: Optional[Redis],
    match_id: uuid.UUID,
    db: Optional[AsyncSession] = None,
) -> Optional[int]:
    """Get remaining seconds for an active match. Falls back to DB started_at if Redis timer missing."""
    if redis is not None:
        timer_val = await redis.get(RedisKey.match_timer(str(match_id)))
        if timer_val:
            expiry = float(timer_val)
            return max(0, int(expiry - time.time()))

    # Fallback: compute from DB started_at + duration
    if db is not None:
        try:
            match = await get_match(db, match_id)
            if match.status != MatchStatus.ACTIVE or not match.started_at:
                return None
            started_at = match.started_at
            if started_at.tzinfo is None:
                started_at = started_at.replace(tzinfo=timezone.utc)
            elapsed = (datetime.now(timezone.utc) - started_at).total_seconds()
            return max(0, int(match.duration_seconds - elapsed))
        except Exception:
            return None
    return None


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
        match = await _lock_active_match_for_completion(db, match_id)
        if match is None:
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
            # Update ELO ratings (match row still locked FOR UPDATE)
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
        match = await _lock_active_match_for_completion(db, match_id)
        if match is None:
            return {}

        # Update ELO ratings (match row still locked FOR UPDATE)
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
        match = await _lock_active_match_for_completion(db, match_id)
        if match is None:
            return {}

        # Verify forfeiter is a participant and determine winner
        if forfeiter_id == match.player1_id:
            winner_id = match.player2_id
        elif forfeiter_id == match.player2_id:
            winner_id = match.player1_id
        else:
            raise NotMatchParticipant()

        # Update ELO ratings (match row still locked FOR UPDATE)
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


async def match_has_inflight_submissions(db: AsyncSession, match: Match) -> bool:
    """True if either player still has QUEUED/RUNNING submissions for this match."""
    result = await db.execute(
        select(func.count())
        .select_from(Submission)
        .where(
            (Submission.match_id == match.id)
            & (Submission.user_id.in_([match.player1_id, match.player2_id]))
            & (Submission.status.in_([SubmissionStatus.QUEUED, SubmissionStatus.RUNNING]))
        )
    )
    return int(result.scalar() or 0) > 0


async def check_and_complete_expired_matches(
    db: AsyncSession, redis: Optional[Redis]
) -> list[dict]:
    """
    Scan for expired active matches and complete them.
    Called periodically by the matchmaking worker / Redis poller.

    Returns list of match result dicts (same shape as complete_match) for WS broadcast.
    Falls back to DB started_at when Redis timer is missing.
    Defers timeout while either player has QUEUED/RUNNING submissions.
    """
    result = await db.execute(
        select(Match)
        .where(Match.status == MatchStatus.ACTIVE)
        .options(
            selectinload(Match.player1),
            selectinload(Match.player2),
            selectinload(Match.problem),
            selectinload(Match.match_problems).selectinload(MatchProblem.problem),
        )
    )
    matches = result.scalars().all()
    completed_results = []

    for match in matches:
        remaining = await get_remaining_time(redis, match.id, db=db)
        if remaining is None:
            # No Redis timer and couldn't compute — use started_at directly
            if match.started_at:
                started_at = match.started_at
                if started_at.tzinfo is None:
                    started_at = started_at.replace(tzinfo=timezone.utc)
                elapsed = (datetime.now(timezone.utc) - started_at).total_seconds()
                remaining = max(0, int(match.duration_seconds - elapsed))
            else:
                continue

        if remaining <= 0:
            if await match_has_inflight_submissions(db, match):
                logger.info(
                    "[MATCH] Deferring timeout for %s — submissions still in flight",
                    match.id,
                )
                continue
            result_data = await complete_match(db, redis, match.id, reason="timeout")
            if result_data:
                completed_results.append(result_data)

    return completed_results


async def _determine_winner(db: AsyncSession, match: Match) -> Optional[uuid.UUID]:
    """
    Determine winner based on submissions (timeout / complete_match path).

    Rules (multi-problem):
    1. Player who has ACCEPTED on all match problems wins
    2. If both have all → earliest timestamp of their last required AC wins
    3. If neither completed the set → most problems solved wins; equal → draw
    Legacy single-problem matches still work (set size 1).
    """
    problem_ids = get_match_problem_ids(match)
    if not problem_ids:
        return None

    needed = len(problem_ids)

    result = await db.execute(
        select(Submission)
        .where(
            (Submission.match_id == match.id)
            & (Submission.status == SubmissionStatus.ACCEPTED)
            & (Submission.problem_id.in_(problem_ids))
        )
        .order_by(Submission.judged_at.asc())
    )
    accepted_submissions = list(result.scalars().all())
    if not accepted_submissions:
        return None

    # Track distinct accepted problems per user and when they completed the set
    solved: dict[uuid.UUID, set[uuid.UUID]] = {}
    completed_at: dict[uuid.UUID, datetime] = {}

    for sub in accepted_submissions:
        bucket = solved.setdefault(sub.user_id, set())
        if sub.problem_id in bucket:
            continue
        bucket.add(sub.problem_id)
        if len(bucket) >= needed and sub.user_id not in completed_at:
            completed_at[sub.user_id] = sub.judged_at or sub.submitted_at

    if completed_at:
        # Earliest to finish all problems (full-set AC win path)
        return min(completed_at.items(), key=lambda item: item[1])[0]

    # Partial timeout: prefer most problems solved; tie → draw
    p1_count = len(solved.get(match.player1_id, set()))
    p2_count = len(solved.get(match.player2_id, set()))
    if p1_count > p2_count:
        return match.player1_id
    if p2_count > p1_count:
        return match.player2_id
    return None


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
        "problem_titles": [p.title for p in get_ordered_match_problems(match)],
        "player1_username": match.player1.username,
        "player2_username": match.player2.username,
        "winner_username": match.winner.username if match.winner else None,
        "reason": "completed",
        "started_at": match.started_at.isoformat() if match.started_at else None,
        "ended_at": match.ended_at.isoformat() if match.ended_at else None,
        "player1_elo_delta": (match.player1_elo_after or 0) - match.player1_elo_before,
        "player2_elo_delta": (match.player2_elo_after or 0) - match.player2_elo_before,
    }
