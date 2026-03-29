"""
Backfill LeetCode signature metadata for matchmaking problems.

Why:
Some legacy problem rows do not have method_name / parameters / return_type,
so the battle editor falls back to CP-style main() templates.

Usage:
    python -m backend.scripts.backfill_matchmaking_signatures
"""

import asyncio
import argparse
import json
import logging
from dataclasses import dataclass
from pathlib import Path

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.config import settings
from backend.models.problem import Problem

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Signature:
    method_name: str
    parameters: list[dict]
    return_type: str


# Title aliases are matched case-insensitively.
SIGNATURES_BY_TITLE: dict[str, Signature] = {
    # Existing seeded matchmaking problems.
    "3 sum": Signature("threeSum", [{"name": "nums", "type": "int[]"}], "int[][]"),
    "print the matrix in spiral manner": Signature("spiralOrder", [{"name": "matrix", "type": "int[][]"}], "int[]"),
    "spiral matrix": Signature("spiralOrder", [{"name": "matrix", "type": "int[][]"}], "int[]"),
    "spiral printer": Signature("spiralOrder", [{"name": "matrix", "type": "int[][]"}], "int[]"),
    "longest substring without repeating characters": Signature("lengthOfLongestSubstring", [{"name": "s", "type": "str"}], "int"),
    "max consecutive ones iii": Signature("longestOnes", [{"name": "nums", "type": "int[]"}, {"name": "k", "type": "int"}], "int"),
    "maximum points you can obtain from cards": Signature("maxScore", [{"name": "cardScore", "type": "int[]"}, {"name": "k", "type": "int"}], "int"),
    "sort an array of 0's 1's and 2's": Signature("sortColors", [{"name": "nums", "type": "int[]"}], "int[]"),
    "find minimum in rotated sorted array": Signature("findMin", [{"name": "nums", "type": "int[]"}], "int"),

    # Legacy / common title variants seen in older datasets.
    "two sum": Signature("twoSum", [{"name": "nums", "type": "int[]"}, {"name": "target", "type": "int"}], "int[]"),
    "target pair": Signature("twoSum", [{"name": "nums", "type": "int[]"}, {"name": "target", "type": "int"}], "bool"),
    "binary to decimal": Signature("binaryToDecimal", [{"name": "s", "type": "str"}], "int"),
}


def _write_template_file(template_path: str, missing_rows: list[dict]) -> None:
    path = Path(template_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(missing_rows, indent=2), encoding="utf-8")


async def backfill_signatures(template_path: str | None = None) -> None:
    engine = create_async_engine(settings.database_url, echo=False)
    Session = async_sessionmaker(engine, expire_on_commit=False)

    async with Session() as db:
        lower_titles = list(SIGNATURES_BY_TITLE.keys())

        result = await db.execute(
            select(Problem).where(func.lower(Problem.title).in_(lower_titles))
        )
        problems = list(result.scalars().all())

        if not problems:
            logger.warning("No matchmaking problem rows matched configured title aliases.")
            await engine.dispose()
            return

        updated_count = 0
        for problem in problems:
            sig = SIGNATURES_BY_TITLE.get(problem.title.lower())
            if sig is None:
                continue

            old_tuple = (
                problem.method_name,
                json.dumps(problem.parameters, sort_keys=True) if problem.parameters else None,
                problem.return_type,
            )
            new_tuple = (
                sig.method_name,
                json.dumps(sig.parameters, sort_keys=True),
                sig.return_type,
            )

            if old_tuple == new_tuple:
                logger.info("Unchanged: %s", problem.title)
                continue

            problem.method_name = sig.method_name
            problem.parameters = sig.parameters
            problem.return_type = sig.return_type
            updated_count += 1
            logger.info("Updated signature: %s -> %s(%s) -> %s", problem.title, sig.method_name, sig.parameters, sig.return_type)

        await db.commit()
        logger.info("Done. Updated %d row(s).", updated_count)

        # Visibility: print active problems still missing signatures after this pass.
        missing_result = await db.execute(
            select(
                Problem.id,
                Problem.title,
                Problem.method_name,
                Problem.parameters,
                Problem.return_type,
            )
            .where(Problem.is_active == True, Problem.method_name.is_(None))
            .order_by(Problem.title.asc())
        )
        missing_rows_raw = missing_result.fetchall()
        missing_titles = [row[1] for row in missing_rows_raw]

        if missing_titles:
            logger.warning("Active problems still missing signatures: %d", len(missing_titles))
            for title in missing_titles:
                logger.warning(" - %s", title)

            if template_path:
                missing_rows = [
                    {
                        "id": str(row[0]),
                        "title": row[1],
                        "method_name": row[2],
                        "parameters": row[3],
                        "return_type": row[4],
                        "suggested_mapping": {
                            "method_name": "",
                            "parameters": [],
                            "return_type": "",
                        },
                    }
                    for row in missing_rows_raw
                ]
                _write_template_file(template_path, missing_rows)
                logger.info("Wrote template for missing signatures to: %s", template_path)
        else:
            logger.info("All active problems have signature metadata.")

    await engine.dispose()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Backfill signature metadata for matchmaking problems")
    parser.add_argument(
        "--template-path",
        default="backend/scripts/matchmaking_signature_template.json",
        help="Path to write missing-signature template JSON",
    )
    parser.add_argument(
        "--no-template",
        action="store_true",
        help="Do not write template file for unresolved active problems",
    )
    args = parser.parse_args()

    template = None if args.no_template else args.template_path
    asyncio.run(backfill_signatures(template_path=template))
