"""
Seed the hardcoded string company pack.
"""

import asyncio
import logging

from backend.scripts import seed_count_and_say
from backend.scripts import seed_custom_sort_string
from backend.scripts import seed_decode_string
from backend.scripts import seed_find_the_index_of_the_first_occurrence_in_a_string
from backend.scripts import seed_group_anagrams
from backend.scripts import seed_integer_to_roman
from backend.scripts import seed_isomorphic_strings
from backend.scripts import seed_longest_common_prefix
from backend.scripts import seed_longest_palindromic_substring
from backend.scripts import seed_minimum_remove_to_make_valid_parentheses
from backend.scripts import seed_multiply_strings
from backend.scripts import seed_palindromic_substrings
from backend.scripts import seed_regular_expression_matching
from backend.scripts import seed_roman_to_integer
from backend.scripts import seed_simplify_path
from backend.scripts import seed_string_to_integer_atoi
from backend.scripts import seed_valid_anagram
from backend.scripts import seed_valid_number
from backend.scripts import seed_word_break
from backend.scripts import seed_zigzag_conversion

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SEEDERS = [
    ("Longest Common Prefix", seed_longest_common_prefix.seed),
    ("Valid Anagram", seed_valid_anagram.seed),
    ("Isomorphic Strings", seed_isomorphic_strings.seed),
    ("Roman to Integer", seed_roman_to_integer.seed),
    ("Integer to Roman", seed_integer_to_roman.seed),
    ("Find the Index of the First Occurrence in a String", seed_find_the_index_of_the_first_occurrence_in_a_string.seed),
    ("Zigzag Conversion", seed_zigzag_conversion.seed),
    ("String to Integer (atoi)", seed_string_to_integer_atoi.seed),
    ("Group Anagrams", seed_group_anagrams.seed),
    ("Decode String", seed_decode_string.seed),
    ("Longest Palindromic Substring", seed_longest_palindromic_substring.seed),
    ("Palindromic Substrings", seed_palindromic_substrings.seed),
    ("Multiply Strings", seed_multiply_strings.seed),
    ("Minimum Remove to Make Valid Parentheses", seed_minimum_remove_to_make_valid_parentheses.seed),
    ("Custom Sort String", seed_custom_sort_string.seed),
    ("Simplify Path", seed_simplify_path.seed),
    ("Count and Say", seed_count_and_say.seed),
    ("Word Break", seed_word_break.seed),
    ("Valid Number", seed_valid_number.seed),
    ("Regular Expression Matching", seed_regular_expression_matching.seed),
]


async def seed() -> None:
    for title, seeder in SEEDERS:
        logger.info("Seeding string problem: %s", title)
        await seeder()


if __name__ == "__main__":
    asyncio.run(seed())
