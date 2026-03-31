"""
Seed the hardcoded LeetCode-style linked-list company pack.
"""

import asyncio
import logging

from backend.scripts import seed_merge_two_sorted_lists
from backend.scripts import seed_middle_of_linked_list
from backend.scripts import seed_palindrome_linked_list
from backend.scripts import seed_remove_nth_from_end
from backend.scripts import seed_reverse_linked_list
from backend.scripts import seed_reverse_linked_list_ii

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SEEDERS = [
    ("Reverse Linked List", seed_reverse_linked_list.seed),
    ("Merge Two Sorted Lists", seed_merge_two_sorted_lists.seed),
    ("Middle of the Linked List", seed_middle_of_linked_list.seed),
    ("Remove Nth Node From End of List", seed_remove_nth_from_end.seed),
    ("Palindrome Linked List", seed_palindrome_linked_list.seed),
    ("Reverse Linked List II", seed_reverse_linked_list_ii.seed),
]


async def seed() -> None:
    for title, seeder in SEEDERS:
        logger.info("Seeding linked-list problem: %s", title)
        await seeder()


if __name__ == "__main__":
    asyncio.run(seed())
