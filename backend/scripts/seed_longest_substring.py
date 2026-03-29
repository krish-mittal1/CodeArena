import asyncio
import json
import logging

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from backend.config import settings
from backend.core.constants import Difficulty
from backend.models.problem import Problem
from backend.models.test_case import TestCase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TITLE = "Longest Substring Without Repeating Characters"


def length_of_longest_substring(s: str) -> int:
    """Reference solution using sliding window."""
    char_index = {}
    max_len = 0
    start = 0
    
    for end, char in enumerate(s):
        if char in char_index and char_index[char] >= start:
            start = char_index[char] + 1
        char_index[char] = end
        max_len = max(max_len, end - start + 1)
    
    return max_len


def make_case(s: str, order_index: int, is_sample: bool = False) -> dict:
    """Generate test case JSON."""
    output = length_of_longest_substring(s)
    return {
        "input": json.dumps({"s": s}),
        "output": json.dumps(output),
        "order_index": order_index,
        "is_sample": is_sample,
    }


def build_test_cases() -> list:
    """Build 150+ test cases: samples + edge cases + patterns + randomized."""
    cases = []
    
    # 1. Sample cases from problem statement (2)
    cases.append(make_case("abcabcbb", 0, True))  # Output: 3 ("abc")
    cases.append(make_case("bbbbb", 1, True))     # Output: 1 ("b")
    
    idx = 2
    
    # 2. Edge cases (20)
    cases.append(make_case("", idx, False))       # Empty string
    idx += 1
    cases.append(make_case("a", idx, False))      # Single char
    idx += 1
    cases.append(make_case("ab", idx, False))     # Two chars, no repeat
    idx += 1
    cases.append(make_case("aa", idx, False))     # Two same chars
    idx += 1
    cases.append(make_case("aaa", idx, False))    # All same chars
    idx += 1
    cases.append(make_case("abcdef", idx, False)) # All unique, ascending
    idx += 1
    cases.append(make_case("fedcba", idx, False)) # All unique, descending
    idx += 1
    cases.append(make_case("abcabc", idx, False)) # Repeating pattern
    idx += 1
    cases.append(make_case("dvdf", idx, False))   # Mixed lengths
    idx += 1
    cases.append(make_case("au", idx, False))     # Two unique
    idx += 1
    cases.append(make_case("aab", idx, False))    # Repeat at start
    idx += 1
    cases.append(make_case("baa", idx, False))    # Repeat at end
    idx += 1
    cases.append(make_case("aba", idx, False))    # Repeat separated
    idx += 1
    cases.append(make_case("abcabcabcabcd", idx, False))  # Long repeat pattern
    idx += 1
    cases.append(make_case("tmmzuxt", idx, False))  # Complex mid-pattern
    idx += 1
    cases.append(make_case("a" * 100, idx, False)) # 100 same chars
    idx += 1
    cases.append(make_case("abcdefghijklmnopqrstuvwxyz", idx, False))  # Alphabet
    idx += 1
    cases.append(make_case("zyxwvutsrqponmlkjihgfedcba", idx, False))  # Reverse alphabet
    idx += 1
    cases.append(make_case("0123456789", idx, False))  # Digits
    idx += 1
    cases.append(make_case(" ", idx, False))   # Space
    idx += 1
    cases.append(make_case("a a a a", idx, False))  # Spaces between chars
    idx += 1
    
    # 3. Patterned arrays (40)
    patterns = [
        "abcdefghijklmnopqr",    # Long ascending
        "abcabcabcabcabc",       # Repeating "abc"
        "abcdabcdabcdabcd",      # Repeating "abcd"
        "aabbccdd",              # Pairs
        "ababababab" * 2,        # Alternating
        "xyz" * 5,               # Triple repeats
        "!@#$%^&*()",            # Special chars
    ]
    
    for pattern in patterns:
        for k_mult in [1, 2, 3]:
            if len(pattern) * k_mult <= 1000:
                test_str = pattern * k_mult
                cases.append(make_case(test_str, idx, False))
                idx += 1
            if idx >= 2 + 20 + 42:  # Limit to 42 patterned cases
                break
        if idx >= 2 + 20 + 42:
            break
    
    # Fill remaining pattern slots if needed
    while idx < 2 + 20 + 42:
        test_str = "abcdefghij" * ((idx - 22) % 3 + 1)
        cases.append(make_case(test_str, idx, False))
        idx += 1
    
    # 4. Randomized deterministic cases (88 more to reach 150+)
    rng_seed = 20260329
    for i in range(88):
        rng_seed = (rng_seed * 1103515245 + 12345) & 0x7fffffff
        
        # Vary length: 5, 10, 20, 50, 100, 150
        length_choices = [5, 10, 20, 50, 100, 150]
        length = length_choices[rng_seed % len(length_choices)]
        
        # Generate string with controlled repeat rate
        rng_seed = (rng_seed * 1103515245 + 12345) & 0x7fffffff
        repeat_rate = rng_seed % 100  # 0-99
        
        chars = []
        charset_size = 5 if repeat_rate < 30 else (10 if repeat_rate < 70 else 26)
        
        for j in range(length):
            rng_seed = (rng_seed * 1103515245 + 12345) & 0x7fffffff
            char_idx = rng_seed % charset_size
            chars.append(chr(ord('a') + char_idx))
        
        test_str = ''.join(chars)
        cases.append(make_case(test_str, idx, False))
        idx += 1
    
    assert len(cases) >= 150, f"Expected 150+ cases, got {len(cases)}"
    return cases


async def seed():
    """Seed or update the problem."""
    engine = create_async_engine(settings.database_url, echo=False)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async with session_factory() as db:
        # Check if problem exists
        result = await db.execute(
            select(Problem).where(Problem.title == TITLE)
        )
        problem = result.scalar_one_or_none()

        description = (
            "Given a string s, find the length of the longest substring without repeating characters.\n\n"
            "A substring is a contiguous sequence of characters within a string.\n\n"
            "Example 1:\n"
            "Input: s = \"abcabcbb\"\n"
            "Output: 3\n"
            "Explanation: The answer is \"abc\", with length 3.\n\n"
            "Example 2:\n"
            "Input: s = \"bbbbb\"\n"
            "Output: 1\n"
            "Explanation: The answer is \"b\", with length 1.\n\n"
            "Example 3:\n"
            "Input: s = \"pwwkew\"\n"
            "Output: 3\n"
            "Explanation: The answer is \"wke\", with length 3. Note that the answer must be a substring, \"pwke\" is a subsequence and not a substring."
        )
        
        input_format = (
            "Line 1: string s (0 <= length <= 5 * 10^4)"
        )
        
        constraints = (
            "0 <= s.length <= 5 * 10^4\n"
            "s consists of English letters, digits, symbols and spaces."
        )

        if problem:
            logger.info("Problem exists. Updating metadata and replacing test cases.")
            problem.description = description
            problem.input_format = input_format
            problem.constraints = constraints
            problem.parameters = [
                {"name": "s", "type": "str"},
            ]
            problem.return_type = "int"
            problem.time_limit_ms = 2000
            problem.memory_limit_mb = 256
            problem.rating = 900
            problem.is_active = True

            test_cases_deleted = False
            try:
                await db.execute(delete(TestCase).where(TestCase.problem_id == problem.id))
                await db.flush()
                test_cases_deleted = True
            except Exception as e:
                logger.warning("Could not delete old test cases (referenced by submissions). Keeping existing ones and updating metadata only.")
                await db.rollback()
                await db.refresh(problem)
        else:
            logger.info("Creating new problem entry.")
            problem = Problem(
                title=TITLE,
                description=description,
                difficulty=Difficulty.EASY,
                input_format=input_format,
                output_format="Single integer: length of longest substring without repeating characters",
                constraints=constraints,
                method_name="lengthOfLongestSubstring",
                parameters=[
                    {"name": "s", "type": "str"},
                ],
                return_type="int",
                time_limit_ms=2000,
                memory_limit_mb=256,
                rating=900,
                is_active=True,
            )
            db.add(problem)
            await db.flush()
            test_cases_deleted = True

        # Only add new test cases if this is a new problem or we successfully deleted old ones
        if test_cases_deleted:
            test_cases = build_test_cases()
            for tc in test_cases:
                db.add(TestCase(problem_id=problem.id, **tc))
            await db.commit()
            logger.info("Seeded '%s' with %d test cases.", TITLE, len(test_cases))
        else:
            # Just commit the metadata update
            await db.commit()
            logger.info("Updated metadata for '%s'. Test cases kept from previous seeding.", TITLE)

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
