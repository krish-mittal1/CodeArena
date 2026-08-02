"""
Problem service — problem CRUD and ELO-based selection for matches.
"""

import random
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

# Candidate pool size when sampling for a battle slot.
_PICK_CANDIDATE_LIMIT = 64


async def create_problem(db: AsyncSession, data: ProblemCreate) -> Problem:
    """Create a new problem with test cases."""
    problem = Problem(
        title=data.title,
        description=data.description,
        difficulty=data.difficulty.value,
        input_format=data.input_format,
        output_format=data.output_format,
        constraints=data.constraints,
        problem_type=data.problem_type,
        rating=data.rating,
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
    """List all active DSA problems (CP track is retired from product surfaces)."""
    result = await db.execute(
        select(Problem)
        .where(Problem.is_active == True)
        .where(Problem.problem_type == "dsa")
        .order_by(Problem.created_at.desc())
        .options(selectinload(Problem.test_cases))
    )
    return result.scalars().all()


async def get_active_problem_catalog(
    db: AsyncSession,
    problem_type: str | None = None,
) -> Sequence[Problem]:
    """List active problems without loading heavy test-case/sample data.

    Defaults to DSA-only. Explicit `problem_type` still filters when provided.
    """
    query = (
        select(Problem)
        .where(Problem.is_active == True)
        .order_by(Problem.created_at.desc())
    )

    # CP is removed from product catalogs; default to DSA when unspecified.
    effective_type = problem_type or "dsa"
    query = query.where(Problem.problem_type == effective_type)

    result = await db.execute(query)
    return result.scalars().all()


async def get_random_problem(db: AsyncSession) -> Problem:
    """Select a random active problem for a match (fallback, no ELO filtering)."""
    result = await db.execute(
        select(Problem)
        .where(Problem.is_active == True)
        .where(Problem.problem_type == "dsa")
        .order_by(func.random())
        .limit(1)
        .options(selectinload(Problem.test_cases))
    )
    problem = result.scalar_one_or_none()
    if not problem:
        raise ProblemNotFound()
    return problem


def _target_rating_for_elo(avg_elo: int) -> int:
    """Ideal problem rating for a match given the players' average Elo."""
    if avg_elo < 400:
        return 850
    if avg_elo < 800:
        return 1050
    return 1175


def _elo_rating_bands(avg_elo: int) -> tuple[tuple[int, int], list[tuple[int, int]]]:
    """
    ELO → primary rating band + fill order for multi-problem selection.

    Contiguous bands so newly synced DSA packs (800–1450) participate:

      0–400   → Easy   (800–950)
      400–800 → Medium (950–1200)
      800+    → Hard   (1100–1450)  — includes harder practice for high Elo
    """
    easy, medium, hard = (800, 950), (950, 1200), (1100, 1450)
    if avg_elo < 400:
        return easy, [medium, hard, easy]
    if avg_elo < 800:
        return medium, [easy, hard, medium]
    return hard, [medium, easy, hard]


def _weighted_pick(
    candidates: list[Problem],
    *,
    target_rating: int,
    prefer_topics: set[str],
) -> Problem:
    """Pick one candidate preferring Elo closeness and unused topics."""
    from backend.services.interview_metadata_service import get_problem_meta

    if not candidates:
        raise ValueError("candidates must be non-empty")

    weights: list[float] = []
    for p in candidates:
        dist = abs((p.rating or target_rating) - target_rating)
        # Closer to target Elo rating ⇒ higher weight; soft so distant packs still appear.
        w = 1.0 / (1.0 + dist / 100.0)
        topic = get_problem_meta(p.title)["topic"]
        if prefer_topics and topic not in prefer_topics:
            w *= 2.5
        elif prefer_topics and topic in prefer_topics:
            w *= 0.35
        weights.append(max(w, 0.01))

    return random.choices(candidates, weights=weights, k=1)[0]


async def _pick_dsa_problem(
    db: AsyncSession,
    *,
    rating_low: int | None = None,
    rating_high: int | None = None,
    exclude_ids: set[uuid.UUID] | None = None,
    prefer_topics: set[str] | None = None,
    target_rating: int | None = None,
) -> Problem | None:
    """Pick one active DSA problem with Elo-weighted preference and topic diversity."""
    exclude_ids = exclude_ids or set()
    prefer_topics = prefer_topics or set()
    target = target_rating if target_rating is not None else 1050

    conditions = [
        Problem.is_active == True,  # noqa: E712
        Problem.problem_type == "dsa",
    ]
    if rating_low is not None:
        conditions.append(Problem.rating >= rating_low)
    if rating_high is not None:
        conditions.append(Problem.rating <= rating_high)
    if exclude_ids:
        conditions.append(Problem.id.notin_(exclude_ids))

    result = await db.execute(
        select(Problem)
        .where(and_(*conditions))
        .order_by(func.random())
        .limit(_PICK_CANDIDATE_LIMIT)
        .options(selectinload(Problem.test_cases))
    )
    candidates = list(result.scalars().all())
    if not candidates:
        return None

    return _weighted_pick(
        candidates,
        target_rating=target,
        prefer_topics=prefer_topics,
    )


async def get_problem_for_match(db: AsyncSession, avg_elo: int) -> Problem:
    """
    Select a random active problem appropriate for the players' skill level.
    Kept for callers that still need a single problem; battles use get_problems_for_match.
    """
    problems = await get_problems_for_match(db, avg_elo, count=1)
    return problems[0]


async def get_problems_for_match(
    db: AsyncSession, avg_elo: int, count: int = 3
) -> list[Problem]:
    """
    Select `count` distinct active DSA problems for a battle.

    Prefers the players' Elo rating band for the first problem, then fills from
    nearby bands / the full active DSA pool with Elo-weighted preference while
    avoiding duplicates and preferring diverse topics when metadata is available.

    New packages must be synced (`python -m backend.tools.sync_problems --all`)
    before they appear here.
    """
    from backend.services.interview_metadata_service import get_problem_meta

    if count < 1:
        raise ValueError("count must be >= 1")

    primary_band, fill_order = _elo_rating_bands(avg_elo)
    target = _target_rating_for_elo(avg_elo)
    selected: list[Problem] = []
    used_ids: set[uuid.UUID] = set()
    used_topics: set[str] = set()

    primary = await _pick_dsa_problem(
        db,
        rating_low=primary_band[0],
        rating_high=primary_band[1],
        exclude_ids=used_ids,
        target_rating=target,
    )
    if primary:
        selected.append(primary)
        used_ids.add(primary.id)
        used_topics.add(get_problem_meta(primary.title)["topic"])
        logger.info(
            f"[PROBLEM] Primary '{primary.title}' (rating={primary.rating}) "
            f"for avg_elo={avg_elo} (band {primary_band[0]}-{primary_band[1]})"
        )

    for low, high in fill_order:
        if len(selected) >= count:
            break
        pick = await _pick_dsa_problem(
            db,
            rating_low=low,
            rating_high=high,
            exclude_ids=used_ids,
            prefer_topics=used_topics,
            target_rating=target,
        )
        if pick:
            selected.append(pick)
            used_ids.add(pick.id)
            used_topics.add(get_problem_meta(pick.title)["topic"])

    # Soft window around target (±250) so nearby out-of-band packs still compete.
    if len(selected) < count:
        pick = await _pick_dsa_problem(
            db,
            rating_low=max(700, target - 250),
            rating_high=target + 275,
            exclude_ids=used_ids,
            prefer_topics=used_topics,
            target_rating=target,
        )
        if pick:
            selected.append(pick)
            used_ids.add(pick.id)
            used_topics.add(get_problem_meta(pick.title)["topic"])

    # Full active DSA pool with Elo-weighted preference (newly synced packs included).
    while len(selected) < count:
        pick = await _pick_dsa_problem(
            db,
            exclude_ids=used_ids,
            prefer_topics=used_topics,
            target_rating=target,
        )
        if not pick:
            break
        selected.append(pick)
        used_ids.add(pick.id)
        used_topics.add(get_problem_meta(pick.title)["topic"])

    if not selected:
        raise ProblemNotFound()

    if len(selected) < count:
        logger.warning(
            f"[PROBLEM] Only found {len(selected)}/{count} DSA problems for avg_elo={avg_elo}"
        )
    else:
        titles = ", ".join(f"{p.title}({p.rating})" for p in selected)
        logger.info(f"[PROBLEM] Selected {count} problems for avg_elo={avg_elo}: {titles}")

    return selected


async def get_test_cases(db: AsyncSession, problem_id: uuid.UUID) -> Sequence[TestCase]:
    """Get ordered test cases for a problem."""
    result = await db.execute(
        select(TestCase)
        .where(TestCase.problem_id == problem_id)
        .order_by(TestCase.order_index)
    )
    return result.scalars().all()
