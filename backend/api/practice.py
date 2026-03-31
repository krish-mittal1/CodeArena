"""
Practice routes — submit code for solo practice (no match required).
"""

import uuid
import logging
from sqlalchemy import select

from fastapi import APIRouter, Depends, HTTPException, status
from redis.asyncio import Redis

from backend.db.session import get_db, AsyncSession
from backend.dependencies import get_current_user, get_redis
from backend.models.user import User
from backend.core.constants import Language
from backend.models.test_case import TestCase
from backend.execution.sandbox import sandbox
from backend.services.judge_service import judge
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


class PracticeRunRequest(BaseModel):
    problem_id: uuid.UUID
    code: str = Field(..., min_length=1, max_length=50000)
    language: Language


class PracticeRunCaseResult(BaseModel):
    order_index: int
    verdict: str
    input: str
    expected_output: str
    actual_output: Optional[str] = None
    error_output: Optional[str] = None
    execution_time_ms: int = 0
    memory_used_kb: int = 0


class PracticeRunResponse(BaseModel):
    status: str
    passed_test_cases: int
    total_test_cases: int
    execution_time_ms: int
    memory_used_kb: int
    cases: list[PracticeRunCaseResult]


@router.post("/run", response_model=PracticeRunResponse)
async def practice_run(
    data: PracticeRunRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Run code against sample test cases only (LeetCode-style Run)."""
    problem = await problem_service.get_problem_by_id(db, data.problem_id)
    if not problem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Problem not found.",
        )

    sample_result = await db.execute(
        select(TestCase)
        .where(
            TestCase.problem_id == data.problem_id,
            TestCase.is_sample.is_(True),
        )
        .order_by(TestCase.order_index)
    )
    sample_cases = list(sample_result.scalars().all())

    if not sample_cases:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No sample test cases available for this problem.",
        )

    problem_meta = None
    if problem.method_name:
        problem_meta = {
            "method_name": problem.method_name,
            "parameters": problem.parameters,
            "return_type": problem.return_type,
        }

    batch_results = await sandbox.execute_batch(
        language=data.language.value,
        code=data.code,
        test_inputs=[tc.input for tc in sample_cases],
        time_limit_ms=problem.time_limit_ms or 2000,
        memory_limit_mb=problem.memory_limit_mb or 256,
        problem_meta=problem_meta,
    )

    passed = 0
    max_time_ms = 0
    max_memory_kb = 0
    overall_status = "accepted"
    case_results: list[PracticeRunCaseResult] = []

    for tc, run_result in zip(sample_cases, batch_results):
        if run_result.stage == "compile" and run_result.exit_code != 0:
            verdict = "compilation_error"
            actual_output = ""
            error_output = run_result.stderr[:2000]
        else:
            verdict = judge(
                actual_output=run_result.stdout,
                expected_output=tc.expected_output,
                exit_code=run_result.exit_code,
                timed_out=run_result.timed_out,
                oom_killed=run_result.oom_killed,
                problem_title=problem.title,
                is_leetcode_mode=problem_meta is not None,
            ).value
            actual_output = run_result.stdout[:2000]
            error_output = run_result.stderr[:2000] if run_result.stderr else None

        max_time_ms = max(max_time_ms, run_result.time_ms)
        max_memory_kb = max(max_memory_kb, run_result.memory_kb)

        if verdict == "accepted":
            passed += 1
        elif overall_status == "accepted":
            overall_status = verdict

        case_results.append(
            PracticeRunCaseResult(
                order_index=tc.order_index,
                verdict=verdict,
                input=tc.input,
                expected_output=tc.expected_output,
                actual_output=actual_output,
                error_output=error_output,
                execution_time_ms=run_result.time_ms,
                memory_used_kb=run_result.memory_kb,
            )
        )

    logger.info(
        "[Practice] Run completed for user=%s problem=%s (%d/%d sample cases passed)",
        current_user.id,
        data.problem_id,
        passed,
        len(sample_cases),
    )

    return PracticeRunResponse(
        status=overall_status,
        passed_test_cases=passed,
        total_test_cases=len(sample_cases),
        execution_time_ms=max_time_ms,
        memory_used_kb=max_memory_kb,
        cases=case_results,
    )


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
    Analyze a completed submission using AI.
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
        submission_id=str(submission.id),
    )

    logger.info(
        f"[AI] Analysis completed for submission {submission.id} "
        f"(status={submission.status})"
    )

    return analysis
