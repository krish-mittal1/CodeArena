"""
Practice routes — submit code for solo practice (no match required).
"""

import uuid
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from redis.asyncio import Redis

from backend.db.session import get_db, AsyncSession
from backend.dependencies import get_current_user, get_redis
from backend.models.user import User
from backend.core.constants import Language
from backend.schemas.submission import SubmissionResponse
from backend.services import submission_service, problem_service

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/practice", tags=["Practice"])


class PracticeSubmissionCreate(BaseModel):
    problem_id: uuid.UUID
    code: str = Field(..., min_length=1, max_length=50000)
    language: Language


@router.post("/submit", response_model=SubmissionResponse, status_code=201)
async def practice_submit(
    data: PracticeSubmissionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    redis: Redis | None = Depends(get_redis),
):
    """Submit code for a practice problem (no match required)."""
    # Validate problem exists
    problem = await problem_service.get_problem_by_id(db, data.problem_id)
    if not problem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Problem not found.",
        )

    submission = await submission_service.create_practice_submission(
        db=db,
        user_id=current_user.id,
        problem_id=data.problem_id,
        code=data.code,
        language=data.language.value,
        redis=redis,
    )

    logger.info(
        f"[Practice] Submission {submission.id} created "
        f"(problem={data.problem_id}, user={current_user.id})"
    )

    return submission


@router.get("/submissions/{problem_id}", response_model=list[SubmissionResponse])
async def get_practice_submissions(
    problem_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get the current user's practice submissions for a specific problem."""
    submissions = await submission_service.get_practice_submissions(
        db, current_user.id, problem_id
    )
    return submissions
