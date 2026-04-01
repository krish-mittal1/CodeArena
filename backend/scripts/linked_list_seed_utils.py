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
def merge_sorted(a: list[int], b: list[int]) -> list[int]:
    i = 0
    j = 0
    out: list[int] = []
    while i < len(a) and j < len(b):
        if a[i] <= b[j]:
            out.append(a[i])
            i += 1
        else:
            out.append(b[j])
            j += 1
    out.extend(a[i:])
    out.extend(b[j:])
    return out


async def upsert_problem(db: AsyncSession, title: str, kwargs: dict, cases: Iterable[dict]) -> None:
    result = await db.execute(select(Problem).where(Problem.title == title))
    problem = result.scalar_one_or_none()

    if problem:
        for key, value in kwargs.items():
            setattr(problem, key, value)
        deleted = False
        try:
            await db.execute(delete(TestCase).where(TestCase.problem_id == problem.id))
            await db.flush()
            deleted = True
        except Exception:
            await db.rollback()
            await db.refresh(problem)
    else:
        problem = Problem(title=title, **kwargs)
        db.add(problem)
        await db.flush()
        deleted = True

    if deleted:
        for test_case in cases:
            db.add(TestCase(problem_id=problem.id, **test_case))

    await db.commit()
