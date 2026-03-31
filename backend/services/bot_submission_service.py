"""
Bot auto-submission service - automatically submit code for bot players.

Behavior goals:
  - believable delay before first submit
  - stronger bots prefer stronger languages and get second attempts
  - weaker bots are more likely to make one bad attempt and stop
  - bots use the same submission pipeline as real players
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone

from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.models.match import Match
from backend.models.submission import Submission
from backend.services import bot_service, submission_service

logger = logging.getLogger(__name__)


class BotSubmissionState:
    """Track per-bot state inside a match."""

    KEY_TEMPLATE = "bot:state:{match_id}:{user_id}"
    LOCK_TEMPLATE = "bot:lock:{match_id}:{user_id}"

    @classmethod
    def get_key(cls, match_id: str, user_id: str) -> str:
        return cls.KEY_TEMPLATE.format(match_id=match_id, user_id=user_id)

    @classmethod
    def get_lock_key(cls, match_id: str, user_id: str) -> str:
        return cls.LOCK_TEMPLATE.format(match_id=match_id, user_id=user_id)


def _decode(value, default: str = "") -> str:
    if value is None:
        return default
    if isinstance(value, bytes):
        return value.decode()
    return str(value)


async def check_and_submit_bot_code(
    db: AsyncSession,
    redis: Redis,
    match_id: uuid.UUID,
) -> None:
    """
    Check if either player is a bot, and if so, decide whether that bot should
    submit now.
    """
    match_id_str = str(match_id)

    try:
        result = await db.execute(
            select(Match)
            .where(Match.id == match_id)
            .options(
                selectinload(Match.player1),
                selectinload(Match.player2),
                selectinload(Match.problem),
            )
        )
        match = result.scalar_one_or_none()

        if not match:
            logger.warning("[BOT] Match %s not found", match_id_str)
            return

        if not match.player1.is_bot and not match.player2.is_bot:
            return

        if match.player1.is_bot:
            await _try_bot_submission(db, redis, match, match.player1_id, match.player1)

        if match.player2.is_bot:
            await _try_bot_submission(db, redis, match, match.player2_id, match.player2)

    except Exception as e:
        logger.error("[BOT] Error checking bot submissions for %s: %s", match_id_str, e, exc_info=True)


async def _get_latest_submission(
    db: AsyncSession,
    match_id: uuid.UUID,
    user_id: uuid.UUID,
) -> Submission | None:
    result = await db.execute(
        select(Submission)
        .where(
            Submission.match_id == match_id,
            Submission.user_id == user_id,
        )
        .order_by(Submission.submitted_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def _try_bot_submission(
    db: AsyncSession,
    redis: Redis,
    match: Match,
    user_id: uuid.UUID,
    user,
) -> None:
    user_id_str = str(user_id)
    match_id_str = str(match.id)
    profile = bot_service.get_profile_for_username(user.username)
    lock_key = BotSubmissionState.get_lock_key(match_id_str, user_id_str)

    if profile is None:
        logger.warning("[BOT] No profile found for %s", user.username)
        return

    acquired = await redis.set(lock_key, "1", nx=True, ex=15)
    if not acquired:
        return

    try:
        latest_submission = await _get_latest_submission(db, match.id, user_id)
        if latest_submission and latest_submission.status in {"queued", "running", "accepted"}:
            return

        difficulty = getattr(match.problem, "difficulty", None)
        max_attempts = bot_service.get_bot_max_attempts(profile, difficulty)
        state_key = BotSubmissionState.get_key(match_id_str, user_id_str)
        raw_state = await redis.hgetall(state_key)
        state = {_decode(key): _decode(value) for key, value in raw_state.items()}

        attempts = int(state.get("attempts", "0"))
        next_due_at = float(state.get("next_due_at", "0") or 0)
        selected_language = state.get("language", "")

        if attempts >= max_attempts:
            return

        if not match.started_at:
            return

        started_at = match.started_at
        if started_at.tzinfo is None:
            started_at = started_at.replace(tzinfo=timezone.utc)

        now = datetime.now(timezone.utc).timestamp()

        if not next_due_at:
            delay = bot_service.get_bot_submit_delay_seconds(
                profile=profile,
                difficulty=difficulty,
                attempt_index=attempts,
                match_duration_seconds=match.duration_seconds or 900,
            )
            next_due_at = started_at.timestamp() + delay
            selected_language = bot_service.choose_language(profile, match.problem.title, attempts)
            await redis.hset(
                state_key,
                mapping={
                    "attempts": str(attempts),
                    "next_due_at": str(next_due_at),
                    "language": selected_language,
                },
            )
            await redis.expire(state_key, 3600)

        if now < next_due_at:
            logger.debug("[BOT] %s is still thinking for %.1fs", user.username, next_due_at - now)
            return

        code, is_likely_correct = bot_service.BotCodeGenerator.generate_solution(
            problem_title=match.problem.title,
            language=selected_language or bot_service.choose_language(profile, match.problem.title, attempts),
            difficulty=difficulty,
            bot_profile=profile,
            attempt_index=attempts,
        )

        submission = await submission_service.create_submission(
            db=db,
            match_id=match.id,
            user_id=user_id,
            problem_id=match.problem_id,
            code=code,
            language=selected_language or bot_service.choose_language(profile, match.problem.title, attempts),
            redis=redis,
        )

        attempts += 1
        follow_up_due_at = 0.0

        if attempts < max_attempts and not is_likely_correct:
            follow_up_delay = bot_service.get_bot_submit_delay_seconds(
                profile=profile,
                difficulty=difficulty,
                attempt_index=attempts,
                match_duration_seconds=match.duration_seconds or 900,
            )
            follow_up_due_at = now + follow_up_delay

        await redis.hset(
            state_key,
            mapping={
                "attempts": str(attempts),
                "next_due_at": str(follow_up_due_at),
                "language": selected_language or bot_service.choose_language(profile, match.problem.title, attempts),
            },
        )
        await redis.expire(state_key, 3600)

        logger.info(
            "[BOT] %s submitted for match %s (attempt=%s/%s, likely_correct=%s, submission_id=%s)",
            user.username,
            match.id,
            attempts,
            max_attempts,
            is_likely_correct,
            submission.id,
        )

    except Exception as e:
        logger.error("[BOT] Failed to submit for %s: %s", user.username, e, exc_info=True)
    finally:
        await redis.delete(lock_key)


async def process_bot_submissions_for_active_matches(
    db: AsyncSession,
    redis: Redis,
) -> int:
    """
    Scan all active matches and process bot submissions.
    Returns the number of active matches checked.
    """
    count = 0

    try:
        result = await db.execute(select(Match).where(Match.status == "active"))
        active_matches = result.scalars().all()

        for match in active_matches:
            await check_and_submit_bot_code(db, redis, match.id)
            count += 1

    except Exception as e:
        logger.error("[BOT] Error processing bot submissions: %s", e, exc_info=True)

    return count
