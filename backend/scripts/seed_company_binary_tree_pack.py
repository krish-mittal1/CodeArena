import asyncio
import logging

from backend.scripts import (
    seed_even_more_binary_tree_problems,
    seed_more_binary_tree_problems,
    seed_yet_more_binary_tree_problems,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SEEDERS = [
    ("Binary Tree Ladder", seed_more_binary_tree_problems.seed),
    ("Extended Binary Tree Ladder", seed_even_more_binary_tree_problems.seed),
    ("Further Binary Tree Ladder", seed_yet_more_binary_tree_problems.seed),
]


async def seed() -> None:
    for title, seeder in SEEDERS:
        logger.info("Seeding binary-tree problem pack: %s", title)
        await seeder()


if __name__ == "__main__":
    asyncio.run(seed())
