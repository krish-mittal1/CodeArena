"""
Submission service — accept code submissions and enqueue for execution.
Supports both Redis queue (production) and in-process queue (dev mode).
"""

import uuid
import json
import logging

from redis.asyncio import Redis
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.constants import SubmissionStatus, RedisKey
from backend.models.submission import Submission
from backend.models.test_case import TestCase

logger = logging.getLogger(__name__)


async def create_submission(
    db: AsyncSession,
    match_id: uuid.UUID,
    user_id: uuid.UUID,
    problem_id: uuid.UUID,
    code: str,
    language: str,
    redis: Redis | None = None,
) -> Submission:
    """
    Create a submission record and enqueue it for async processing.
    Works with Redis (production) or in-process queue (dev mode).
    """
    # Count total test cases for this problem
    result = await db.execute(
        select(func.count(TestCase.id)).where(TestCase.problem_id == problem_id)
    )
    total_test_cases = result.scalar_one()

    submission = Submission(
        match_id=match_id,
        user_id=user_id,
        problem_id=problem_id,
        language=language,
        code=code,
        status=SubmissionStatus.QUEUED,
        total_test_cases=total_test_cases,
    )
    db.add(submission)
    await db.commit()
    await db.refresh(submission)

    # Enqueue for worker processing
    if redis is not None:
        await redis.lpush(
            RedisKey.SUBMISSION_QUEUE,
            json.dumps({"submission_id": str(submission.id)})
        )
        logger.info(f"Submission {submission.id} enqueued to Redis (match={match_id})")
    else:
        # Dev mode — push to in-process asyncio queue
        from backend.workers.judge_worker import dev_queue
        await dev_queue.put(str(submission.id))
        logger.info(f"Submission {submission.id} enqueued to dev queue (match={match_id})")

    return submission


async def get_submission(db: AsyncSession, submission_id: uuid.UUID) -> Submission | None:
    """Get a submission by ID."""
    result = await db.execute(
        select(Submission).where(Submission.id == submission_id)
    )
    return result.scalar_one_or_none()


async def get_match_submissions(
    db: AsyncSession, match_id: uuid.UUID, user_id: uuid.UUID | None = None
) -> list[Submission]:
    """Get submissions for a match, optionally filtered by user."""
    query = select(Submission).where(Submission.match_id == match_id)
    if user_id:
        query = query.where(Submission.user_id == user_id)
    query = query.order_by(Submission.submitted_at.desc())

    result = await db.execute(query)
    return list(result.scalars().all())
