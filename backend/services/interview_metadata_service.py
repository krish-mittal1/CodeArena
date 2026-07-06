"""Load interview metadata (topic, companies, frequency) for progress tracking."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

_DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "problem_metadata.json"

# Hand-curated frequency for high-traffic interview problems
_FREQUENCY_OVERRIDES: dict[str, str] = {
    "Two Sum": "high",
    "Valid Anagram": "high",
    "Valid Palindrome": "high",
    "Merge Intervals": "high",
    "Maximum Subarray": "high",
    "3 Sum": "high",
    "Container With Most Water": "high",
    "Binary Tree Level Order Traversal": "high",
    "Invert Binary Tree": "high",
    "Lowest Common Ancestor of a Binary Tree": "high",
    "Longest Substring Without Repeating Characters": "high",
    "Group Anagrams": "high",
    "Product of Array Except Self": "high",
    "Jump Game": "medium",
    "Merge Two Sorted Lists": "high",
    "Reverse Linked List": "high",
    "Search in Rotated Sorted Array": "high",
    "Word Break": "medium",
    "Coin Change": "medium",
}


@lru_cache(maxsize=1)
def _load_metadata() -> dict[str, dict]:
    if not _DATA_PATH.is_file():
        return {}
    return json.loads(_DATA_PATH.read_text(encoding="utf-8"))


def get_problem_meta(title: str) -> dict:
    meta = _load_metadata().get(title, {})
    topic = meta.get("topic") or "Arrays"
    companies = meta.get("companies") or []
    frequency = _FREQUENCY_OVERRIDES.get(title, meta.get("frequency", "medium"))
    return {"topic": topic, "companies": companies, "frequency": frequency}


def all_topics() -> list[str]:
    topics = {get_problem_meta(t)["topic"] for t in _load_metadata()}
    return sorted(topics)
