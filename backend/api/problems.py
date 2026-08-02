"""
Problem routes — CRUD (admin) and listing.
"""

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select

from backend.db.session import get_db, AsyncSession
from backend.dependencies import get_current_user, get_admin_user, get_optional_current_user
from backend.models.user import User
from backend.models.submission import Submission
from backend.schemas.problem import (
    ProblemCreate,
    ProblemPublic,
    ProblemAdmin,
    ProblemCatalogPublic,
    TestCasePublic,
)
from backend.services import problem_service
from backend.core.constants import SubmissionStatus

router = APIRouter(prefix="/problems", tags=["Problems"])


@router.post("/", response_model=ProblemPublic, status_code=201)
async def create_problem(
    data: ProblemCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_admin_user),  # ✓ FIXED: Admin-only access
):
    """Create a new problem with test cases. Admin only."""
    problem = await problem_service.create_problem(db, data)
    return _to_public(problem)


@router.get("/", response_model=list[ProblemPublic])
async def list_problems(
    db: AsyncSession = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    """List all active problems."""
    problems = await problem_service.get_active_problems(db)
    solved_ids = await _get_solved_problem_ids(db, current_user.id) if current_user else set()
    return [_to_public(p, solved=(p.id in solved_ids)) for p in problems]


@router.get("/catalog", response_model=list[ProblemCatalogPublic])
async def list_problem_catalog(
    problem_type: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    """List active problems with a lightweight payload for catalogs and filters."""
    problems = await problem_service.get_active_problem_catalog(db, problem_type=problem_type)
    solved_ids = await _get_solved_problem_ids(db, current_user.id) if current_user else set()
    return [
        ProblemCatalogPublic(
            id=problem.id,
            title=problem.title,
            difficulty=problem.difficulty,
            problem_type=getattr(problem, "problem_type", "dsa"),
            rating=getattr(problem, "rating", 800),
            solved=(problem.id in solved_ids),
        )
        for problem in problems
    ]


@router.get("/{problem_id}", response_model=ProblemPublic)
async def get_problem(
    problem_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    """Get a specific problem (public view with sample test cases only)."""
    problem = await problem_service.get_problem_by_id(db, problem_id)
    solved_ids = await _get_solved_problem_ids(db, current_user.id, {problem.id}) if current_user else set()
    return _to_public(problem, solved=(problem.id in solved_ids))


async def _get_solved_problem_ids(
    db: AsyncSession,
    user_id: uuid.UUID,
    limit_to: set[uuid.UUID] | None = None,
) -> set[uuid.UUID]:
    query = select(Submission.problem_id).where(
        Submission.user_id == user_id,
        Submission.status == SubmissionStatus.ACCEPTED,
    ).distinct()

    if limit_to:
        query = query.where(Submission.problem_id.in_(limit_to))

    result = await db.execute(query)
    return set(result.scalars().all())


def _to_public(problem, solved: bool = False) -> ProblemPublic:
    """Convert problem model to public schema with only sample test cases."""
    from backend.schemas.problem import ProblemExamplePublic, ProblemImagePublic

    presentation = getattr(problem, "presentation", None) or {}
    presentation_examples = presentation.get("examples") if isinstance(presentation, dict) else None
    presentation_images = presentation.get("images") if isinstance(presentation, dict) else None

    sample_cases_raw = [
        tc
        for tc in (problem.test_cases if hasattr(problem, "test_cases") and problem.test_cases else [])
        if tc.is_sample
    ]

    sample_cases = []
    examples = []
    for i, tc in enumerate(sample_cases_raw):
        overlay = (
            presentation_examples[i]
            if isinstance(presentation_examples, list) and i < len(presentation_examples)
            else None
        )
        explanation = None
        if isinstance(overlay, dict):
            explanation = overlay.get("explanation")
        sample_cases.append(
            TestCasePublic(
                input=tc.input,
                expected_output=tc.expected_output,
                order_index=tc.order_index,
                explanation=explanation,
            )
        )
        examples.append(
            ProblemExamplePublic(
                input=(overlay.get("input") if isinstance(overlay, dict) and overlay.get("input") else tc.input),
                output=(
                    overlay.get("output")
                    if isinstance(overlay, dict) and overlay.get("output")
                    else tc.expected_output
                ),
                explanation=explanation,
            )
        )

    # Presentation-only examples beyond sample count (display only, never executed)
    if isinstance(presentation_examples, list) and len(presentation_examples) > len(sample_cases_raw):
        for overlay in presentation_examples[len(sample_cases_raw) :]:
            if not isinstance(overlay, dict):
                continue
            if not overlay.get("input") and not overlay.get("output"):
                continue
            examples.append(
                ProblemExamplePublic(
                    input=overlay.get("input") or "",
                    output=overlay.get("output") or "",
                    explanation=overlay.get("explanation"),
                )
            )

    # Fallback: derive examples from samples when presentation missing (pre-sync)
    if not examples and sample_cases:
        examples = [
            ProblemExamplePublic(
                input=tc.input,
                output=tc.expected_output,
                explanation=tc.explanation,
            )
            for tc in sample_cases
        ]

    images = []
    if isinstance(presentation_images, list):
        for img in presentation_images:
            if isinstance(img, dict) and img.get("src"):
                images.append(ProblemImagePublic(src=img["src"], alt=img.get("alt")))

    return ProblemPublic(
        id=problem.id,
        title=problem.title,
        description=problem.description,
        difficulty=problem.difficulty,
        input_format=problem.input_format,
        output_format=problem.output_format,
        constraints=problem.constraints,
        problem_type=getattr(problem, "problem_type", "dsa"),
        rating=getattr(problem, "rating", 800),
        time_limit_ms=problem.time_limit_ms,
        memory_limit_mb=problem.memory_limit_mb,
        method_name=getattr(problem, "method_name", None),
        parameters=getattr(problem, "parameters", None),
        return_type=getattr(problem, "return_type", None),
        solved=solved,
        sample_cases=sample_cases,
        examples=examples,
        images=images,
    )
