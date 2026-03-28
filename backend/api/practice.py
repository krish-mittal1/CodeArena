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
from backend.services import ai_service

from pydantic import BaseModel, Field
from typing import Optional, Any

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/practice", tags=["Practice"])


class PracticeSubmissionCreate(BaseModel):
    problem_id: uuid.UUID
    code: str = Field(..., min_length=1, max_length=50000)
    language: Language


class AIAnalyzeRequest(BaseModel):
    submission_id: uuid.UUID
    problem_id: uuid.UUID


@router.post("/submit", response_model=SubmissionResponse, status_code=201)
async def practice_submit(
    data: PracticeSubmissionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    redis: Optional[Redis] = Depends(get_redis),
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


@router.post("/analyze")
async def analyze_submission(
    data: AIAnalyzeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Analyze a completed submission using Gemini AI.
    Returns structured feedback: verdict explanation, TC/SC, issues,
    optimized approach, improved code, and tips.
    """
    from sqlalchemy import select
    from backend.models.submission import Submission

    # Fetch submission (must belong to current user)
    result = await db.execute(
        select(Submission).where(
            Submission.id == data.submission_id,
            Submission.user_id == current_user.id,
        )
    )
    submission = result.scalar_one_or_none()
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission not found.",
        )

    # Fetch problem
    problem = await problem_service.get_problem_by_id(db, data.problem_id)
    if not problem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Problem not found.",
        )

    # Extract failed test case info if available
    failed_input = None
    expected_output = None
    actual_output = None
    error_output = None

    if submission.failed_test_case:
        ftc = submission.failed_test_case
        if isinstance(ftc, dict):
            failed_input = ftc.get("input")
            expected_output = ftc.get("expected_output")
            actual_output = ftc.get("actual_output")
            error_output = ftc.get("error_output")
        else:
            failed_input = getattr(ftc, "input", None)
            expected_output = getattr(ftc, "expected_output", None)
            actual_output = getattr(ftc, "actual_output", None)
            error_output = getattr(ftc, "error_output", None)

    analysis = await ai_service.analyze_code(
        problem_title=problem.title,
        problem_description=problem.description,
        constraints=getattr(problem, "constraints", None),
        language=submission.language,
        code=submission.code,
        verdict_status=submission.status,
        failed_input=failed_input,
        expected_output=expected_output,
        actual_output=actual_output,
        error_output=error_output,
    )

    logger.info(
        f"[AI] Analysis completed for submission {submission.id} "
        f"(status={submission.status})"
    )

    return analysis
