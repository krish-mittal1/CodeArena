"""
Seed script — insert 10 competitive programming problems with test cases.

Usage:
    python -m backend.scripts.seed_problems
"""

import asyncio
import logging

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import select

from backend.config import settings
from backend.db.base import Base
from backend.models.problem import Problem
from backend.models.test_case import TestCase
from backend.core.constants import Difficulty

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Problem Definitions
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PROBLEMS = [
    # ── 1. Two Sum (competitive version) ─────────────────────
    {
        "title": "Two Sum",
        "difficulty": Difficulty.EASY,
        "description": (
            "You are given an integer n, an integer target, and an array of n integers.\n"
            "Determine whether there exist two distinct indices i and j such that:\n"
            "arr[i] + arr[j] = target.\n"
            "If such a pair exists print YES, otherwise print NO."
        ),
        "input_format": "n target\n"
                        "a1 a2 ... an",
        "output_format": "Print YES or NO.",
        "constraints": "1 ≤ n ≤ 2×10^5, -10^9 ≤ a[i], target ≤ 10^9",
        "time_limit_ms": 1000,
        "memory_limit_mb": 256,
        "test_cases": [
            # Visible (sample) test cases
            {"input": "4 9\n2 7 11 15", "expected_output": "YES", "is_sample": True, "order_index": 0},
            {"input": "3 10\n1 2 3", "expected_output": "NO", "is_sample": True, "order_index": 1},
            # Hidden test cases
            {"input": "5 0\n-1 -2 -3 1 4", "expected_output": "YES", "is_sample": False, "order_index": 2},
            {"input": "1 5\n5", "expected_output": "NO", "is_sample": False, "order_index": 3},
            {"input": "6 8\n4 4 2 6 1 7", "expected_output": "YES", "is_sample": False, "order_index": 4},
        ],
    },
    # ── 2. FizzBuzz ─────────────────────────────────────────
    {
        "title": "FizzBuzz",
        "difficulty": Difficulty.EASY,
        "description": (
            "Given an integer N, print numbers from 1 to N. "
            "For multiples of 3 print 'Fizz', for multiples of 5 print 'Buzz', "
            "for multiples of both print 'FizzBuzz'."
        ),
        "input_format": "A single integer N.",
        "output_format": "N lines, each containing the number or Fizz/Buzz/FizzBuzz.",
        "constraints": "1 ≤ N ≤ 100",
        "time_limit_ms": 1000,
        "memory_limit_mb": 128,
        "test_cases": [
            {"input": "5", "expected_output": "1\n2\nFizz\n4\nBuzz", "is_sample": True, "order_index": 0},
            {"input": "15", "expected_output": "1\n2\nFizz\n4\nBuzz\nFizz\n7\n8\nFizz\nBuzz\n11\nFizz\n13\n14\nFizzBuzz", "is_sample": True, "order_index": 1},
            {"input": "1", "expected_output": "1", "is_sample": False, "order_index": 2},
            {"input": "3", "expected_output": "1\n2\nFizz", "is_sample": False, "order_index": 3},
        ],
    },
    # ── 3. Palindrome Check ─────────────────────────────────
    {
        "title": "Palindrome Check",
        "difficulty": Difficulty.EASY,
        "description": (
            "Given a string S consisting of lowercase English letters, "
            "determine if it is a palindrome.\n\n"
            "Print 'YES' if it is a palindrome, 'NO' otherwise."
        ),
        "input_format": "A single string S.",
        "output_format": "'YES' or 'NO'.",
        "constraints": "1 ≤ |S| ≤ 10^5",
        "time_limit_ms": 1000,
        "memory_limit_mb": 128,
        "test_cases": [
            {"input": "racecar", "expected_output": "YES", "is_sample": True, "order_index": 0},
            {"input": "hello", "expected_output": "NO", "is_sample": True, "order_index": 1},
            {"input": "a", "expected_output": "YES", "is_sample": False, "order_index": 2},
            {"input": "abba", "expected_output": "YES", "is_sample": False, "order_index": 3},
            {"input": "abcba", "expected_output": "YES", "is_sample": False, "order_index": 4},
        ],
    },
    # ── 4. Maximum Subarray Sum ─────────────────────────────
    {
        "title": "Maximum Subarray Sum",
        "difficulty": Difficulty.MEDIUM,
        "description": (
            "Given an array of N integers, find the contiguous subarray "
            "with the maximum sum. Print the maximum sum.\n\n"
            "The subarray must contain at least one element."
        ),
        "input_format": "First line: N.\nSecond line: N space-separated integers.",
        "output_format": "A single integer — the maximum subarray sum.",
        "constraints": "1 ≤ N ≤ 10^5, -10^4 ≤ a[i] ≤ 10^4",
        "time_limit_ms": 2000,
        "memory_limit_mb": 256,
        "test_cases": [
            {"input": "9\n-2 1 -3 4 -1 2 1 -5 4", "expected_output": "6", "is_sample": True, "order_index": 0},
            {"input": "1\n-1", "expected_output": "-1", "is_sample": True, "order_index": 1},
            {"input": "5\n1 2 3 4 5", "expected_output": "15", "is_sample": False, "order_index": 2},
            {"input": "4\n-1 -2 -3 -4", "expected_output": "-1", "is_sample": False, "order_index": 3},
            {"input": "6\n2 -1 2 3 4 -5", "expected_output": "10", "is_sample": False, "order_index": 4},
        ],
    },
    # ── 5. Reverse Words ────────────────────────────────────
    {
        "title": "Reverse Words",
        "difficulty": Difficulty.EASY,
        "description": (
            "Given a string of words separated by single spaces, "
            "reverse the order of the words.\n\n"
            "There are no leading or trailing spaces."
        ),
        "input_format": "A single line containing a string of words.",
        "output_format": "The words in reversed order, separated by spaces.",
        "constraints": "1 ≤ total length ≤ 10^4",
        "time_limit_ms": 1000,
        "memory_limit_mb": 128,
        "test_cases": [
            {"input": "hello world", "expected_output": "world hello", "is_sample": True, "order_index": 0},
            {"input": "the sky is blue", "expected_output": "blue is sky the", "is_sample": True, "order_index": 1},
            {"input": "a", "expected_output": "a", "is_sample": False, "order_index": 2},
            {"input": "Alice Bob Charlie", "expected_output": "Charlie Bob Alice", "is_sample": False, "order_index": 3},
        ],
    },
    # ── 6. Count Primes ─────────────────────────────────────
    {
        "title": "Count Primes",
        "difficulty": Difficulty.MEDIUM,
        "description": (
            "Given an integer N, count the number of prime numbers "
            "strictly less than N.\n\n"
            "Use the Sieve of Eratosthenes for efficiency."
        ),
        "input_format": "A single integer N.",
        "output_format": "A single integer — the count of primes less than N.",
        "constraints": "0 ≤ N ≤ 5 × 10^6",
        "time_limit_ms": 3000,
        "memory_limit_mb": 256,
        "test_cases": [
            {"input": "10", "expected_output": "4", "is_sample": True, "order_index": 0},
            {"input": "0", "expected_output": "0", "is_sample": True, "order_index": 1},
            {"input": "1", "expected_output": "0", "is_sample": False, "order_index": 2},
            {"input": "2", "expected_output": "0", "is_sample": False, "order_index": 3},
            {"input": "100", "expected_output": "25", "is_sample": False, "order_index": 4},
        ],
    },
    # ── 7. Binary Search ────────────────────────────────────
    {
        "title": "Binary Search",
        "difficulty": Difficulty.EASY,
        "description": (
            "Given a sorted array of N distinct integers and a target value T, "
            "find the 0-based index of T in the array.\n\n"
            "If T is not found, print -1."
        ),
        "input_format": "First line: N and T.\nSecond line: N sorted integers.",
        "output_format": "A single integer — the index, or -1.",
        "constraints": "1 ≤ N ≤ 10^5, -10^9 ≤ values ≤ 10^9",
        "time_limit_ms": 1000,
        "memory_limit_mb": 128,
        "test_cases": [
            {"input": "5 3\n1 2 3 4 5", "expected_output": "2", "is_sample": True, "order_index": 0},
            {"input": "3 6\n1 2 3", "expected_output": "-1", "is_sample": True, "order_index": 1},
            {"input": "1 1\n1", "expected_output": "0", "is_sample": False, "order_index": 2},
            {"input": "6 -5\n-10 -5 0 5 10 15", "expected_output": "1", "is_sample": False, "order_index": 3},
        ],
    },
    # ── 8. Longest Common Subsequence ───────────────────────
    {
        "title": "Longest Common Subsequence",
        "difficulty": Difficulty.MEDIUM,
        "description": (
            "Given two strings A and B, find the length of their "
            "longest common subsequence (LCS).\n\n"
            "A subsequence is a sequence that appears in the same relative "
            "order but not necessarily contiguous."
        ),
        "input_format": "First line: string A.\nSecond line: string B.",
        "output_format": "A single integer — the LCS length.",
        "constraints": "1 ≤ |A|, |B| ≤ 1000",
        "time_limit_ms": 2000,
        "memory_limit_mb": 256,
        "test_cases": [
            {"input": "abcde\nace", "expected_output": "3", "is_sample": True, "order_index": 0},
            {"input": "abc\nabc", "expected_output": "3", "is_sample": True, "order_index": 1},
            {"input": "abc\ndef", "expected_output": "0", "is_sample": False, "order_index": 2},
            {"input": "abcdef\nfbdamn", "expected_output": "2", "is_sample": False, "order_index": 3},
            {"input": "a\na", "expected_output": "1", "is_sample": False, "order_index": 4},
        ],
    },
    # ── 9. Matrix Spiral Order ──────────────────────────────
    {
        "title": "Matrix Spiral Order",
        "difficulty": Difficulty.MEDIUM,
        "description": (
            "Given an M × N matrix of integers, print all elements "
            "in spiral order (clockwise from top-left).\n\n"
            "Print the elements space-separated on a single line."
        ),
        "input_format": "First line: M and N.\nNext M lines: N integers each.",
        "output_format": "All elements in spiral order, space-separated.",
        "constraints": "1 ≤ M, N ≤ 100",
        "time_limit_ms": 1000,
        "memory_limit_mb": 128,
        "test_cases": [
            {"input": "3 3\n1 2 3\n4 5 6\n7 8 9", "expected_output": "1 2 3 6 9 8 7 4 5", "is_sample": True, "order_index": 0},
            {"input": "1 4\n1 2 3 4", "expected_output": "1 2 3 4", "is_sample": True, "order_index": 1},
            {"input": "3 1\n1\n2\n3", "expected_output": "1 2 3", "is_sample": False, "order_index": 2},
            {"input": "2 2\n1 2\n3 4", "expected_output": "1 2 4 3", "is_sample": False, "order_index": 3},
        ],
    },
    # ── 10. Shortest Path (Dijkstra) ────────────────────────
    {
        "title": "Shortest Path",
        "difficulty": Difficulty.HARD,
        "description": (
            "Given a weighted directed graph with N vertices and M edges, "
            "find the shortest path from vertex 1 to vertex N.\n\n"
            "Print the shortest distance. If no path exists, print -1.\n"
            "Vertices are 1-indexed."
        ),
        "input_format": "First line: N M.\nNext M lines: u v w (edge from u to v with weight w).",
        "output_format": "A single integer — shortest distance, or -1.",
        "constraints": "2 ≤ N ≤ 10^5, 0 ≤ M ≤ 2×10^5, 1 ≤ w ≤ 10^9",
        "time_limit_ms": 3000,
        "memory_limit_mb": 256,
        "test_cases": [
            {"input": "5 6\n1 2 2\n1 3 4\n2 3 1\n2 4 7\n3 5 3\n4 5 1", "expected_output": "7", "is_sample": True, "order_index": 0},
            {"input": "3 1\n1 2 5", "expected_output": "-1", "is_sample": True, "order_index": 1},
            {"input": "2 1\n1 2 10", "expected_output": "10", "is_sample": False, "order_index": 2},
            {"input": "4 4\n1 2 1\n2 3 2\n3 4 3\n1 4 10", "expected_output": "6", "is_sample": False, "order_index": 3},
            {"input": "3 0", "expected_output": "-1", "is_sample": False, "order_index": 4},
        ],
    },
]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Seeder
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def seed():
    engine = create_async_engine(settings.database_url, echo=False)
    Session = async_sessionmaker(engine, expire_on_commit=False)

    async with Session() as db:
        for p_data in PROBLEMS:
            test_cases_data = p_data.pop("test_cases")

            # Upsert by title — if problem already exists, skip creating duplicates
            existing = await db.execute(select(Problem).where(Problem.title == p_data["title"]))
            problem = existing.scalar_one_or_none()

            if problem:
                logger.info(f"Skipping existing problem: {problem.title}")
                # Optional: ensure it has at least the defined test cases (no destructive changes)
                continue

            problem = Problem(**p_data)
            db.add(problem)
            await db.flush()

            for tc_data in test_cases_data:
                tc = TestCase(problem_id=problem.id, **tc_data)
                db.add(tc)

            logger.info(f"  ✓ {problem.title} ({len(test_cases_data)} test cases)")

        await db.commit()
        logger.info(f"\n✅ Seeded/updated problems successfully.")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
