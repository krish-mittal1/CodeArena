"""
Update existing problems with LeetCode-style metadata.
Adds method_name, parameters, return_type and converts test cases to JSON format.

Usage: python -m backend.scripts.upgrade_to_leetcode
"""

import asyncio
import json
import logging
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import select, update, text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = "postgresql+asyncpg://postgres:krishisunique@localhost:5432/codearena"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Problem signature definitions
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PROBLEM_SIGNATURES = {
    "Two Sum": {
        "method_name": "twoSum",
        "parameters": [
            {"name": "nums", "type": "int[]"},
            {"name": "target", "type": "int"},
        ],
        "return_type": "bool",
    },
    "Print the matrix in spiral manner": {
        "method_name": "spiralOrder",
        "parameters": [
            {"name": "matrix", "type": "int[][]"},
        ],
        "return_type": "int[]",
    },
    "3 Sum": {
        "method_name": "threeSum",
        "parameters": [
            {"name": "nums", "type": "int[]"},
        ],
        "return_type": "int[][]",
    },
}


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Input converters: old stdin format → JSON lines
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _convert_two_sum_input(raw: str) -> str:
    """
    Old format:
        4 9
        2 7 11 15
    New format (JSON lines):
        [2,7,11,15]
        9
    """
    lines = raw.strip().split("\n")
    first_parts = lines[0].strip().split()
    n = int(first_parts[0])
    target = int(first_parts[1])
    nums = list(map(int, lines[1].strip().split()))
    return json.dumps(nums) + "\n" + json.dumps(target)


def _convert_two_sum_output(raw: str) -> str:
    """
    Old format:
        YES or NO
    New format (JSON):
        true or false
    """
    val = raw.strip().upper()
    return json.dumps(val == "YES")


def _convert_spiral_input(raw: str) -> str:
    """
    Old format:
        3 3
        1 2 3
        4 5 6
        7 8 9
    New format (JSON lines):
        [[1,2,3],[4,5,6],[7,8,9]]
    """
    lines = raw.strip().split("\n")
    dims = lines[0].strip().split()
    rows = int(dims[0])
    matrix = []
    for i in range(1, rows + 1):
        row = list(map(int, lines[i].strip().split()))
        matrix.append(row)
    return json.dumps(matrix)


def _convert_spiral_output(raw: str) -> str:
    """
    Old format:
        1 2 3 6 9 8 7 4 5
    New format (JSON):
        [1,2,3,6,9,8,7,4,5]
    """
    nums = list(map(int, raw.strip().split()))
    return json.dumps(nums)


def _convert_3sum_input(raw: str) -> str:
    """
    Old format:
        6
        -1 0 1 2 -1 -4
    New format (JSON lines):
        [-1,0,1,2,-1,-4]
    """
    lines = raw.strip().split("\n")
    nums = list(map(int, lines[1].strip().split()))
    return json.dumps(nums)


def _convert_3sum_output(raw: str) -> str:
    """
    Old format:
        3
        -1 -1 2
        -1 0 1
    New format (JSON):
        [[-1,-1,2],[-1,0,1]]
    """
    lines = raw.strip().split("\n")
    count = int(lines[0].strip())
    triplets = []
    for i in range(1, count + 1):
        if i < len(lines):
            triplet = list(map(int, lines[i].strip().split()))
            triplets.append(triplet)
    return json.dumps(triplets)


CONVERTERS = {
    "Two Sum": (_convert_two_sum_input, _convert_two_sum_output),
    "Print the matrix in spiral manner": (_convert_spiral_input, _convert_spiral_output),
    "3 Sum": (_convert_3sum_input, _convert_3sum_output),
}


async def upgrade():
    engine = create_async_engine(DATABASE_URL, echo=False)
    Session = async_sessionmaker(engine, expire_on_commit=False)

    async with Session() as db:
        # 1. Update problem signatures
        for title, sig in PROBLEM_SIGNATURES.items():
            result = await db.execute(
                text(
                    "UPDATE problems SET method_name = :mn, parameters = :params, return_type = :rt "
                    "WHERE title = :title"
                ),
                {
                    "mn": sig["method_name"],
                    "params": json.dumps(sig["parameters"]),
                    "rt": sig["return_type"],
                    "title": title,
                }
            )
            logger.info(f"Updated signature for '{title}': {result.rowcount} row(s)")

        # 2. Convert test case formats
        for title, (input_conv, output_conv) in CONVERTERS.items():
            # Fetch problem ID
            prob_result = await db.execute(
                text("SELECT id FROM problems WHERE title = :title"),
                {"title": title}
            )
            prob_row = prob_result.fetchone()
            if not prob_row:
                logger.warning(f"Problem '{title}' not found, skipping test case conversion")
                continue

            problem_id = prob_row[0]

            # Fetch all test cases
            tc_result = await db.execute(
                text("SELECT id, input, expected_output FROM test_cases WHERE problem_id = :pid"),
                {"pid": problem_id}
            )
            test_cases = tc_result.fetchall()
            
            converted = 0
            skipped = 0
            for tc in test_cases:
                tc_id, tc_input, tc_expected = tc
                
                # Skip if already JSON (starts with [ or {)
                stripped_input = tc_input.strip() if tc_input else ""
                if stripped_input.startswith("[") or stripped_input.startswith("{"):
                    skipped += 1
                    continue
                
                try:
                    new_input = input_conv(tc_input)
                    new_output = output_conv(tc_expected)
                    
                    await db.execute(
                        text(
                            "UPDATE test_cases SET input = :inp, expected_output = :out "
                            "WHERE id = :tid"
                        ),
                        {"inp": new_input, "out": new_output, "tid": tc_id}
                    )
                    converted += 1
                except Exception as e:
                    logger.error(f"Failed to convert TC {tc_id} for '{title}': {e}")
                    skipped += 1
            
            logger.info(f"'{title}': converted={converted}, skipped={skipped}")

        await db.commit()
        logger.info("✅ All problems upgraded to LeetCode format!")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(upgrade())
