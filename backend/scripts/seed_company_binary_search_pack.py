import asyncio
import logging

from backend.scripts import seed_capacity_to_ship_packages_within_d_days
from backend.scripts import seed_find_first_and_last_position
from backend.scripts import seed_find_minimum_in_rotated_sorted_array
from backend.scripts import seed_h_index_ii
from backend.scripts import seed_koko_eating_bananas
from backend.scripts import seed_minimum_days_to_make_m_bouquets
from backend.scripts import seed_median_two_sorted_arrays
from backend.scripts import seed_peak_index_in_a_mountain_array
from backend.scripts import seed_search_a_2d_matrix
from backend.scripts import seed_search_in_rotated_sorted_array
from backend.scripts import seed_search_insert_position
from backend.scripts import seed_single_element_in_sorted_array
from backend.scripts import seed_split_array_largest_sum
from backend.scripts import seed_successful_pairs_of_spells_and_potions

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SEEDERS = [
    ("Find Minimum in Rotated Sorted Array", seed_find_minimum_in_rotated_sorted_array.seed),
    ("Search in Rotated Sorted Array", seed_search_in_rotated_sorted_array.seed),
    ("Search Insert Position", seed_search_insert_position.seed),
    ("Koko Eating Bananas", seed_koko_eating_bananas.seed),
    ("Median of Two Sorted Arrays", seed_median_two_sorted_arrays.seed),
    ("Find First and Last Position of Element in Sorted Array", seed_find_first_and_last_position.seed),
    ("Search a 2D Matrix", seed_search_a_2d_matrix.seed),
    ("Peak Index in a Mountain Array", seed_peak_index_in_a_mountain_array.seed),
    ("Single Element in a Sorted Array", seed_single_element_in_sorted_array.seed),
    ("Capacity To Ship Packages Within D Days", seed_capacity_to_ship_packages_within_d_days.seed),
    ("Minimum Number of Days to Make m Bouquets", seed_minimum_days_to_make_m_bouquets.seed),
    ("H-Index II", seed_h_index_ii.seed),
    ("Successful Pairs of Spells and Potions", seed_successful_pairs_of_spells_and_potions.seed),
    ("Split Array Largest Sum", seed_split_array_largest_sum.seed),
]


async def seed() -> None:
    for title, seeder in SEEDERS:
        logger.info("Seeding binary-search problem: %s", title)
        await seeder()


if __name__ == "__main__":
    asyncio.run(seed())
