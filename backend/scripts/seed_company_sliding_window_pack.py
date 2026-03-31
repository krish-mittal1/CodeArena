"""
Seed the hardcoded sliding-window problem pack used by the company pages.

This script runs the existing per-problem seeders so the database contains
the sliding-window problems that are mapped to companies in the frontend.

Usage:
    python -m backend.scripts.seed_company_sliding_window_pack
"""

import asyncio
import logging

from backend.scripts import seed_binary_subarrays_with_sum
from backend.scripts import seed_count_number_of_nice_subarrays
from backend.scripts import seed_fruit_into_baskets
from backend.scripts import seed_longest_repeating_character_replacement
from backend.scripts import seed_longest_substring
from backend.scripts import seed_longest_substring_k_distinct
from backend.scripts import seed_max_consecutive_ones_iii
from backend.scripts import seed_max_points_cards
from backend.scripts import seed_number_of_substrings_containing_all_three_characters

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


SEEDERS = [
    ("Longest Substring Without Repeating Characters", seed_longest_substring.seed),
    ("Longest Repeating Character Replacement", seed_longest_repeating_character_replacement.seed),
    ("Longest Substring With At Most K Distinct Characters", seed_longest_substring_k_distinct.seed),
    ("Fruit Into Baskets", seed_fruit_into_baskets.seed),
    ("Max Consecutive Ones III", seed_max_consecutive_ones_iii.seed),
    ("Binary Subarrays With Sum", seed_binary_subarrays_with_sum.seed),
    ("Count number of Nice subarrays", seed_count_number_of_nice_subarrays.seed),
    ("Number of Substrings Containing All Three Characters", seed_number_of_substrings_containing_all_three_characters.seed),
    ("Maximum Points You Can Obtain from Cards", seed_max_points_cards.seed),
]


async def seed() -> None:
    for title, seeder in SEEDERS:
        logger.info("Seeding sliding-window problem: %s", title)
        await seeder()
    logger.info("Sliding-window company pack seeded successfully (%d problems).", len(SEEDERS))


if __name__ == "__main__":
    asyncio.run(seed())
