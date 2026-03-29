"""
Convert all problems without signature metadata to LeetCode-style I/O contract.

Contract applied:
- method_name = "solve"
- parameters = [{"name": "rawInput", "type": "str"}]
- return_type = "str"

Test case conversion:
- input: raw stdin text -> JSON string
- expected_output: normalized text -> JSON string

This makes frontend snippet generation and backend judge mode consistent for
legacy CP-style problems without manually defining typed signatures per title.

Usage:
    python -m backend.scripts.convert_all_problems_to_leetcode_io
"""

import asyncio
import json
import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.config import settings
from backend.models.problem import Problem
from backend.models.test_case import TestCase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _normalize_output_text(output: str | None) -> str:
    """Mirror legacy judge normalization before wrapping into JSON string."""
    if not output:
        return ""

    lines = [line.rstrip() for line in output.strip().split("\n")]
    while lines and lines[-1] == "":
        lines.pop()
    return "\n".join(lines)


def _to_json_string(value: str | None) -> str:
    return json.dumps(value if value is not None else "")


async def convert_all() -> None:
    engine = create_async_engine(settings.database_url, echo=False)
    Session = async_sessionmaker(engine, expire_on_commit=False)

    async with Session() as db:
        # Convert every problem that still has no LeetCode signature metadata.
        problem_result = await db.execute(
            select(Problem).where(Problem.method_name.is_(None))
        )
        problems = list(problem_result.scalars().all())

        if not problems:
            logger.info("No problems require conversion.")
            await engine.dispose()
            return

        converted_problems = 0
        converted_test_cases = 0

        for problem in problems:
            problem.method_name = "solve"
            problem.parameters = [{"name": "rawInput", "type": "str"}]
            problem.return_type = "str"
            converted_problems += 1

            tc_result = await db.execute(
                select(TestCase).where(TestCase.problem_id == problem.id)
            )
            test_cases = list(tc_result.scalars().all())

            for tc in test_cases:
                # input.txt in driver mode expects one JSON value per line.
                tc.input = _to_json_string(tc.input)

                # Preserve legacy comparison semantics before converting to JSON mode.
                normalized_expected = _normalize_output_text(tc.expected_output)
                tc.expected_output = json.dumps(normalized_expected)
                converted_test_cases += 1

        await db.commit()

        logger.info("Converted problems: %d", converted_problems)
        logger.info("Converted test cases: %d", converted_test_cases)

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(convert_all())
