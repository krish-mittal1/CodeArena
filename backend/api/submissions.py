"""
Submission routes — submit code during a match.
Works in both Redis and dev (no-Redis) modes.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional
from redis.asyncio import Redis

from backend.db.session import get_db, AsyncSession
from backend.dependencies import get_current_user, get_redis
from backend.models.user import User
from backend.core.constants import MatchStatus
from backend.core.submission_rate_limit import ensure_submission_allowed, record_submission
from backend.schemas.submission import SubmissionCreate, SubmissionResponse
from backend.services import submission_service, match_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/submissions", tags=["Submissions"])


@router.post("/", response_model=SubmissionResponse, status_code=201)
async def submit_code(
    data: SubmissionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    redis: Optional[Redis] = Depends(get_redis),
):
    """
    Submit code for a match problem.
    In dev mode (no Redis), validates match from DB instead of Redis state.
    """
    logger.info(
        f"[API] Submission request received "
        f"(match={data.match_id}, user={current_user.id}, lang={data.language.value})"
    )

    # Load match and validate
    match = await match_service.get_match(db, data.match_id)

    # Guard: reject submissions for completed matches
    if match.status == MatchStatus.COMPLETED:
        logger.warning(
            f"[API] Rejected submission for completed match {data.match_id} "
            f"from user {current_user.id}"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Match already completed. No further submissions allowed.",
        )

    # Guard: match must be active
    if match.status != MatchStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Match is not active.",
        )

    # Guard: user must be a participant
    if current_user.id not in (match.player1_id, match.player2_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a participant in this match.",
        )

    # Validate via Redis (production only)
    if redis is not None:
        await match_service.validate_match_active(redis, data.match_id, current_user.id)

    # Conservative anti-spam throttle: max 3 submissions per 5 seconds per user per match.
    ensure_submission_allowed(str(current_user.id), str(data.match_id))

    # Create submission and enqueue (Redis or dev queue)
    submission = await submission_service.create_submission(
        db=db,
        match_id=data.match_id,
        user_id=current_user.id,
        problem_id=match.problem_id,
        code=data.code,
        language=data.language.value,
        redis=redis,
    )
    record_submission(str(current_user.id), str(data.match_id))

    logger.info(
        f"[API] Submission {submission.id} created and enqueued "
        f"(match={data.match_id}, user={current_user.id})"
    )

    return submission
