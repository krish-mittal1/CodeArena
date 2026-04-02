import asyncio
import logging

from backend.scripts.seed_helpful_maths_cf import seed as seed_helpful_maths
from backend.scripts.seed_next_round_cf import seed as seed_next_round
from backend.scripts.seed_team_cf import seed as seed_team
from backend.scripts.seed_watermelon_cf import seed as seed_watermelon
from backend.scripts.seed_way_too_long_words_cf import seed as seed_way_too_long_words

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def seed() -> None:
    seeders = [
        ("Watermelon", seed_watermelon),
        ("Way Too Long Words", seed_way_too_long_words),
        ("Team", seed_team),
        ("Next Round", seed_next_round),
        ("Helpful Maths", seed_helpful_maths),
    ]

    for title, seeder in seeders:
        logger.info("Seeding competitive programming problem: %s", title)
        await seeder()


if __name__ == "__main__":
    asyncio.run(seed())
