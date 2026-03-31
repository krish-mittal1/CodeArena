"""
Seed the hardcoded two-pointers company pack.
"""

import asyncio
import logging

from backend.scripts import seed_3sum
from backend.scripts import seed_container_with_most_water
from backend.scripts import seed_trapping_rain_water
from backend.scripts import seed_two_sum_ii
from backend.scripts import seed_valid_palindrome

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SEEDERS = [
    ("3 Sum", seed_3sum.seed),
    ("Container With Most Water", seed_container_with_most_water.seed),
    ("Trapping Rain Water", seed_trapping_rain_water.seed),
    ("Two Sum II - Input Array Is Sorted", seed_two_sum_ii.seed),
    ("Valid Palindrome", seed_valid_palindrome.seed),
]


async def seed() -> None:
    for title, seeder in SEEDERS:
        logger.info("Seeding two-pointers problem: %s", title)
        await seeder()


if __name__ == "__main__":
    asyncio.run(seed())
