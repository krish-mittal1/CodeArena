"""
Seed the hardcoded LeetCode-style linked-list company pack.
"""

import asyncio
import logging

from backend.scripts import seed_add_two_numbers
from backend.scripts import seed_delete_middle_of_linked_list
from backend.scripts import seed_merge_two_sorted_lists
from backend.scripts import seed_maximum_twin_sum_linked_list
from backend.scripts import seed_middle_of_linked_list
from backend.scripts import seed_odd_even_linked_list
from backend.scripts import seed_palindrome_linked_list
from backend.scripts import seed_partition_list
from backend.scripts import seed_remove_nth_from_end
from backend.scripts import seed_reverse_linked_list
from backend.scripts import seed_reverse_linked_list_ii
from backend.scripts import seed_reverse_nodes_in_k_group
from backend.scripts import seed_rotate_list
from backend.scripts import seed_swap_nodes_in_pairs

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SEEDERS = [
    ("Add Two Numbers", seed_add_two_numbers.seed),
    ("Reverse Linked List", seed_reverse_linked_list.seed),
    ("Merge Two Sorted Lists", seed_merge_two_sorted_lists.seed),
    ("Middle of the Linked List", seed_middle_of_linked_list.seed),
    ("Remove Nth Node From End of List", seed_remove_nth_from_end.seed),
    ("Palindrome Linked List", seed_palindrome_linked_list.seed),
    ("Reverse Linked List II", seed_reverse_linked_list_ii.seed),
    ("Swap Nodes in Pairs", seed_swap_nodes_in_pairs.seed),
    ("Odd Even Linked List", seed_odd_even_linked_list.seed),
    ("Partition List", seed_partition_list.seed),
    ("Rotate List", seed_rotate_list.seed),
    ("Delete the Middle Node of a Linked List", seed_delete_middle_of_linked_list.seed),
    ("Maximum Twin Sum of a Linked List", seed_maximum_twin_sum_linked_list.seed),
    ("Reverse Nodes in k-Group", seed_reverse_nodes_in_k_group.seed),
]


async def seed() -> None:
    for title, seeder in SEEDERS:
        logger.info("Seeding linked-list problem: %s", title)
        await seeder()


if __name__ == "__main__":
    asyncio.run(seed())
