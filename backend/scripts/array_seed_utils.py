from __future__ import annotations

import json
from collections.abc import Iterable

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.problem import Problem
from backend.models.test_case import TestCase


def encode_lines(*values) -> str:
    return "\n".join(json.dumps(value) for value in values)


def make_case(*inputs, expected_output, idx: int, is_sample: bool = False) -> dict:
    return {
        "input": encode_lines(*inputs),
        "expected_output": json.dumps(expected_output),
        "order_index": idx,
        "is_sample": is_sample,
    }


async def upsert_problem(db: AsyncSession, title: str, kwargs: dict, cases: Iterable[dict]) -> None:
    result = await db.execute(
        select(Problem)
        .where(Problem.title == title)
        .order_by(Problem.created_at.asc(), Problem.id.asc())
    )
    problems = list(result.scalars().all())
    problem = problems[0] if problems else None

    if len(problems) > 1:
        for duplicate in problems[1:]:
            duplicate.title = f"{title} [Legacy Duplicate {str(duplicate.id)[:8]}]"
            duplicate.is_active = False
        await db.flush()

    if problem:
        problem_id = problem.id
        for key, value in kwargs.items():
            setattr(problem, key, value)
        await db.flush()
        replace_cases = True
        try:
            await db.execute(delete(TestCase).where(TestCase.problem_id == problem_id))
            await db.flush()
        except Exception:
            await db.rollback()
            result = await db.execute(select(Problem).where(Problem.id == problem_id))
            problem = result.scalar_one()
            for key, value in kwargs.items():
                setattr(problem, key, value)
            await db.flush()
            replace_cases = False
    else:
        problem = Problem(title=title, **kwargs)
        db.add(problem)
        await db.flush()
        replace_cases = True

    if replace_cases:
        for test_case in cases:
            db.add(TestCase(problem_id=problem.id, **test_case))

    await db.commit()
