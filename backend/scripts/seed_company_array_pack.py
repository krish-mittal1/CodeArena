"""
Seed the hardcoded array company pack.
"""

import asyncio
import logging

from backend.scripts import seed_best_time_to_buy_and_sell_stock
from backend.scripts import seed_first_missing_positive
from backend.scripts import seed_game_of_life
from backend.scripts import seed_majority_element
from backend.scripts import seed_maximum_subarray
from backend.scripts import seed_merge_intervals
from backend.scripts import seed_merge_sorted_array
from backend.scripts import seed_next_permutation
from backend.scripts import seed_pascals_triangle
from backend.scripts import seed_product_of_array_except_self
from backend.scripts import seed_rotate_array
from backend.scripts import seed_set_matrix_zeroes
from backend.scripts import seed_two_sum_array

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SEEDERS = [
    ("Two Sum", seed_two_sum_array.seed),
    ("Best Time to Buy and Sell Stock", seed_best_time_to_buy_and_sell_stock.seed),
    ("Maximum Subarray", seed_maximum_subarray.seed),
    ("Merge Sorted Array", seed_merge_sorted_array.seed),
    ("Majority Element", seed_majority_element.seed),
    ("Pascal's Triangle", seed_pascals_triangle.seed),
    ("Product of Array Except Self", seed_product_of_array_except_self.seed),
    ("Rotate Array", seed_rotate_array.seed),
    ("Set Matrix Zeroes", seed_set_matrix_zeroes.seed),
    ("Merge Intervals", seed_merge_intervals.seed),
    ("Next Permutation", seed_next_permutation.seed),
    ("Game of Life", seed_game_of_life.seed),
    ("First Missing Positive", seed_first_missing_positive.seed),
]


async def seed() -> None:
    for title, seeder in SEEDERS:
        logger.info("Seeding array problem: %s", title)
        await seeder()


if __name__ == "__main__":
    asyncio.run(seed())
