"""
Bot auto-submission service — automatically submit code for bot players.

Bot behavior:
  - Random delay: 5-25 seconds after match starts
  - Random code: 40% correct solutions, 60% wrong/incomplete
  - Generates realistic code based on problem type
  - Integrates with existing submission system

Usage (called from workers):
    await bot_submission_service.submit_if_bot_due(db, redis, match_id)
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime, timezone, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from redis.asyncio import Redis

from backend.core.constants import (
    RedisKey, SubmissionStatus, Language, 
    BOT_SUBMISSION_DELAY_MIN, BOT_SUBMISSION_DELAY_MAX
)
from backend.models.match import Match
from backend.models.submission import Submission
from backend.services import submission_service, bot_service

logger = logging.getLogger(__name__)


class BotSubmissionTracker:
    """Track which bots have already submitted in a match."""
    
    TRACKER_KEY = "bot:submissions:{match_id}"
    
    @classmethod
    def get_key(cls, match_id: str) -> str:
        return cls.TRACKER_KEY.format(match_id=match_id)


async def check_and_submit_bot_code(
    db: AsyncSession,
    redis: Redis,
    match_id: uuid.UUID,
) -> None:
    """
    Check if either player is a bot, and if so, generate and submit code.
    
    - Safe to call multiple times (per-bot submission tracking)
    - Generates realistic code (correct/wrong variants)
    - Submits to the same queue as real players
    - Integrates with match completion logic
    """
    match_id_str = str(match_id)
    
    try:
        # Load match with relationships
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
            logger.warning(f"[BOT] Match {match_id_str} not found")
            return
        
        if not match.player1.is_bot and not match.player2.is_bot:
            # No bots in this match
            return
        
        tracker_key = BotSubmissionTracker.get_key(match_id_str)
        
        # Check bot 1
        if match.player1.is_bot:
            await _try_bot_submission(
                db, redis, match, match.player1_id, match.player1, 
                "player1", tracker_key
            )
        
        # Check bot 2
        if match.player2.is_bot:
            await _try_bot_submission(
                db, redis, match, match.player2_id, match.player2,
                "player2", tracker_key
            )
    
    except Exception as e:
        logger.error(f"[BOT] Error checking bot submissions for {match_id_str}: {e}", exc_info=True)


async def _try_bot_submission(
    db: AsyncSession,
    redis: Redis,
    match: Match,
    user_id: uuid.UUID,
    user,
    player_label: str,
    tracker_key: str,
) -> None:
    """Try to submit code for a bot player if it's their turn."""
    
    user_id_str = str(user_id)
    player_key = f"{player_label}:submitted"
    
    # Check if bot already submitted
    already_submitted = await redis.sismember(tracker_key, player_key)
    if already_submitted:
        return
    
    # Calculate if bot should submit now
    match_duration = match.duration_seconds if match.duration_seconds else 900
    
    # Get submission delay: random between BOT_SUBMISSION_DELAY_MIN and BOT_SUBMISSION_DELAY_MAX
    # Store this delay in Redis when match is first created
    delay_key = f"bot:delay:{user_id_str}:{match.id}"
    stored_delay = await redis.get(delay_key)
    
    if stored_delay is None:
        # First time seeing this bot in this match - generate and store delay
        import random
        delay = random.randint(
            BOT_SUBMISSION_DELAY_MIN,
            BOT_SUBMISSION_DELAY_MAX
        )
        await redis.setex(delay_key, 3600, str(delay))  # Store for 1 hour
        stored_delay = str(delay)
    
    delay = int(stored_delay)
    
    # Check elapsed time since match started
    if not match.started_at:
        return
    
    elapsed = (datetime.now(timezone.utc) - match.started_at).total_seconds()
    
    if elapsed < delay:
        # Not time to submit yet
        logger.debug(f"[BOT] {user.username} will submit in {delay - elapsed:.1f}s")
        return
    
    # Time to submit! Generate and submit code
    language = Language.PYTHON  # Default language for bots
    code, _is_likely_correct = bot_service.BotCodeGenerator.generate_solution(
        match.problem.title,
        language
    )
    
    try:
        # Create submission
        submission = await submission_service.create_submission(
            db,
            match.id,
            user_id,
            match.problem_id,
            code,
            language,
            redis=redis,
        )
        
        # Mark bot as submitted in this match
        await redis.sadd(tracker_key, player_key)
        await redis.expire(tracker_key, 3600)  # Expire after 1 hour
        
        logger.info(
            f"[BOT] {user.username} submitted for match {match.id} "
            f"(submission_id={submission.id})"
        )
    
    except Exception as e:
        logger.error(f"[BOT] Failed to submit for {user.username}: {e}", exc_info=True)


async def process_bot_submissions_for_active_matches(
    db: AsyncSession,
    redis: Redis,
) -> int:
    """
    Scan all active matches and process bot submissions.
    Called periodically by the judge worker or a dedicated bot service.
    
    Returns: number of matches checked
    """
    count = 0
    try:
        # Get all active matches from Redis
        # This is a simplified version - adjust based on your actual implementation
        result = await db.execute(
            select(Match)
            .where(Match.status == "active")
        )
        active_matches = result.scalars().all()
        
        for match in active_matches:
            await check_and_submit_bot_code(db, redis, match.id)
            count += 1
    
    except Exception as e:
        logger.error(f"[BOT] Error processing bot submissions: {e}", exc_info=True)
    
    return count
