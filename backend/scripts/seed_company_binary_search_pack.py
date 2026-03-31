"""
Seed the hardcoded binary-search company pack.
"""

import asyncio
import logging

from backend.scripts import add_rotated_array_problem
from backend.scripts import seed_koko_eating_bananas
from backend.scripts import seed_median_two_sorted_arrays
from backend.scripts import seed_search_in_rotated_sorted_array
from backend.scripts import seed_search_insert_position

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SEEDERS = [
    ("Find Minimum in Rotated Sorted Array", add_rotated_array_problem.main),
    ("Search in Rotated Sorted Array", seed_search_in_rotated_sorted_array.seed),
    ("Search Insert Position", seed_search_insert_position.seed),
    ("Koko Eating Bananas", seed_koko_eating_bananas.seed),
    ("Median of Two Sorted Arrays", seed_median_two_sorted_arrays.seed),
]


async def seed() -> None:
    for title, seeder in SEEDERS:
        logger.info("Seeding binary-search problem: %s", title)
        await seeder()


if __name__ == "__main__":
    asyncio.run(seed())
