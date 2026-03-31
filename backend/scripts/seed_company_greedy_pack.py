"""
Seed the hardcoded greedy company pack.
"""

import asyncio
import logging

from backend.scripts import seed_candy
from backend.scripts import seed_gas_station
from backend.scripts import seed_jump_game
from backend.scripts import seed_jump_game_ii
from backend.scripts import seed_non_overlapping_intervals
from backend.scripts import seed_partition_labels

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SEEDERS = [
    ("Jump Game", seed_jump_game.seed),
    ("Jump Game II", seed_jump_game_ii.seed),
    ("Gas Station", seed_gas_station.seed),
    ("Partition Labels", seed_partition_labels.seed),
    ("Non-overlapping Intervals", seed_non_overlapping_intervals.seed),
    ("Candy", seed_candy.seed),
]


async def seed() -> None:
    for title, seeder in SEEDERS:
        logger.info("Seeding greedy problem: %s", title)
        await seeder()


if __name__ == "__main__":
    asyncio.run(seed())
