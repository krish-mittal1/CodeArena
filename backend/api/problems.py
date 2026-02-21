"""
Problem routes — CRUD (admin) and listing.
"""

import uuid

from fastapi import APIRouter, Depends

from backend.db.session import get_db, AsyncSession
from backend.dependencies import get_current_user
from backend.schemas.problem import ProblemCreate, ProblemPublic, ProblemAdmin, TestCasePublic
from backend.services import problem_service

router = APIRouter(prefix="/problems", tags=["Problems"])


@router.post("/", response_model=ProblemPublic, status_code=201)
async def create_problem(
    data: ProblemCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),  # Auth required (admin check can be added)
):
    """Create a new problem with test cases."""
    problem = await problem_service.create_problem(db, data)
    return _to_public(problem)


@router.get("/", response_model=list[ProblemPublic])
async def list_problems(db: AsyncSession = Depends(get_db)):
    """List all active problems."""
    problems = await problem_service.get_active_problems(db)
    return [_to_public(p) for p in problems]


@router.get("/{problem_id}", response_model=ProblemPublic)
async def get_problem(problem_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Get a specific problem (public view with sample test cases only)."""
    problem = await problem_service.get_problem_by_id(db, problem_id)
    return _to_public(problem)


def _to_public(problem) -> ProblemPublic:
    """Convert problem model to public schema with only sample test cases."""
    sample_cases = [
        TestCasePublic(
            input=tc.input,
            expected_output=tc.expected_output,
            order_index=tc.order_index,
        )
        for tc in (problem.test_cases if hasattr(problem, "test_cases") and problem.test_cases else [])
        if tc.is_sample
    ]
    return ProblemPublic(
        id=problem.id,
        title=problem.title,
        description=problem.description,
        difficulty=problem.difficulty,
        input_format=problem.input_format,
        output_format=problem.output_format,
        constraints=problem.constraints,
        time_limit_ms=problem.time_limit_ms,
        memory_limit_mb=problem.memory_limit_mb,
        sample_cases=sample_cases,
    )
