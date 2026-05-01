"""
Problem service — problem CRUD and ELO-based selection for matches.
"""

import uuid
import logging
from typing import Sequence

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.core.exceptions import ProblemNotFound
from backend.models.problem import Problem
from backend.models.test_case import TestCase
from backend.schemas.problem import ProblemCreate

logger = logging.getLogger(__name__)


async def create_problem(db: AsyncSession, data: ProblemCreate) -> Problem:
    """Create a new problem with test cases."""
    problem = Problem(
        title=data.title,
        description=data.description,
        difficulty=data.difficulty.value,
        input_format=data.input_format,
        output_format=data.output_format,
        constraints=data.constraints,
        time_limit_ms=data.time_limit_ms,
        memory_limit_mb=data.memory_limit_mb,
    )
    db.add(problem)
    await db.flush()  # get problem.id

    for tc_data in data.test_cases:
        tc = TestCase(
            problem_id=problem.id,
            input=tc_data.input,
            expected_output=tc_data.expected_output,
            is_sample=tc_data.is_sample,
            order_index=tc_data.order_index,
        )
        db.add(tc)

    await db.commit()
    await db.refresh(problem)
    return problem


async def get_problem_by_id(db: AsyncSession, problem_id: uuid.UUID) -> Problem:
    """Get problem with test cases loaded."""
    result = await db.execute(
        select(Problem)
        .where(Problem.id == problem_id)
        .options(selectinload(Problem.test_cases))
    )
    problem = result.scalar_one_or_none()
    if not problem:
        raise ProblemNotFound()
    return problem


async def get_active_problems(db: AsyncSession) -> Sequence[Problem]:
    """List all active problems."""
    result = await db.execute(
        select(Problem)
        .where(Problem.is_active == True)
        .order_by(Problem.created_at.desc())
        .options(selectinload(Problem.test_cases))
    )
    return result.scalars().all()


async def get_random_problem(db: AsyncSession) -> Problem:
    """Select a random active problem for a match (fallback, no ELO filtering)."""
    result = await db.execute(
        select(Problem)
        .where(Problem.is_active == True)
        .order_by(func.random())
        .limit(1)
        .options(selectinload(Problem.test_cases))
    )
    problem = result.scalar_one_or_none()
    if not problem:
        raise ProblemNotFound()
    return problem


async def get_problem_for_match(db: AsyncSession, avg_elo: int) -> Problem:
    """
    Select a random active problem appropriate for the players' skill level.

    ELO → Problem Rating Band:
      0–400   → Easy   (rating 800–900)
      400–800 → Medium (rating 1000–1100)
      800+    → Hard   (rating 1100–1200)

    Falls back to any random problem if no match in the target band.
    """
    if avg_elo < 400:
        rating_low, rating_high = 800, 900
    elif avg_elo < 800:
        rating_low, rating_high = 1000, 1100
    else:
        rating_low, rating_high = 1100, 1200

    # Try to find a problem in the target rating band
    result = await db.execute(
        select(Problem)
        .where(
            and_(
                Problem.is_active == True,
                Problem.rating >= rating_low,
                Problem.rating <= rating_high,
            )
        )
        .order_by(func.random())
        .limit(1)
        .options(selectinload(Problem.test_cases))
    )
    problem = result.scalar_one_or_none()

    if problem:
        logger.info(
            f"[PROBLEM] Selected '{problem.title}' (rating={problem.rating}) "
            f"for avg_elo={avg_elo} (band {rating_low}-{rating_high})"
        )
        return problem

    # Fallback: any random active problem
    logger.warning(
        f"[PROBLEM] No problem in band {rating_low}-{rating_high} "
        f"for avg_elo={avg_elo}, using random fallback"
    )
    return await get_random_problem(db)


async def get_test_cases(db: AsyncSession, problem_id: uuid.UUID) -> Sequence[TestCase]:
    """Get ordered test cases for a problem."""
    result = await db.execute(
        select(TestCase)
        .where(TestCase.problem_id == problem_id)
        .order_by(TestCase.order_index)
    )
    return result.scalars().all()
