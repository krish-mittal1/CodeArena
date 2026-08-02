"""
Generate frontend/src/data/problemMetadata.js from problems/*/meta.yaml.

Usage: python -m backend.tools.generate_problem_metadata
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import yaml

_REPO = Path(__file__).resolve().parents[2]
_PROBLEMS = _REPO / "problems"
_OUT = _REPO / "frontend" / "src" / "data" / "problemMetadata.js"

_DEFAULT_COMPANIES = [
    "Google", "Amazon", "Microsoft", "Meta", "Apple",
    "Netflix", "Uber", "Adobe", "Oracle", "Goldman Sachs",
    "Flipkart", "Infosys", "TCS", "Wipro", "Accenture",
]

_TOPIC_RULES: list[tuple[str, list[str]]] = [
    ("Linked List", ["linked list", "listnode", "reverse nodes", "remove nth", "merge two sorted lists", "add two numbers", "palindrome linked", "odd even linked", "partition list", "rotate list", "swap nodes", "twin sum", "middle of the linked", "insertion at the head", "deletion of the head", "traversal in linked"]),
    ("Trees", ["binary tree", "binary search tree", "bst", "tree", "leaf", "preorder", "inorder", "zigzag level", "kth smallest", "lowest common ancestor", "symmetric tree", "invert binary", "same tree", "diameter of binary", "max depth", "validate binary", "subtree", "good nodes", "range sum of bst"]),
    ("Graphs", ["island", "graph", "course schedule", "rotting orange", "flood fill", "keys and rooms", "clone graph", "network delay", "pacific atlantic", "surrounded region", "01 matrix", "number of provinces", "bipartite", "max area of island"]),
    ("Dynamic Programming", ["word break", "decode ways", "house robber", "max product", "palindromic substring", "regular expression", "climbing stairs", "coin change", "unique paths", "longest increasing", "partition equal", "min cost climbing", "edit distance", "perfect squares", "fibonacci", "combination sum iv", "longest common subsequence", "triangle"]),
    ("Backtracking", ["combination sum", "subsets", "permutations", "generate parentheses", "letter combinations", "word search", "n queens"]),
    ("Bit Manipulation", ["number of 1 bits", "counting bits", "reverse bits", "sum of two integers", "single number", "power of two", "hamming"]),
    ("Intervals", ["insert interval", "merge intervals", "non-overlapping", "meeting rooms"]),
    ("String", ["string", "anagram", "palindrome", "substring", "regex", "roman", "atoi", "zigzag", "decode string", "permutation in string", "reverse words", "reorganize string"]),
    ("Binary Search", ["binary search", "sorted array", "rotated sorted", "search insert", "mountain array", "median of two", "koko eating", "ship packages", "split array largest", "successful pairs", "find peak", "search a 2d matrix"]),
    ("Sliding Window", ["sliding window", "window maximum", "minimum window", "fruit into baskets", "max consecutive ones", "permutation in string", "nice subarray", "binary subarrays", "find all anagrams"]),
    ("Greedy", ["gas station", "jump game", "candy", "interval", "non-overlapping", "partition labels", "task scheduler", "bouquet", "ipo", "assign cookies", "lemonade", "flowers", "balloons", "refueling", "bag of tokens"]),
    ("Matrix", ["matrix", "spiral", "set matrix", "game of life", "search a 2d", "rotate image", "valid sudoku", "surrounded"]),
    ("Hash Map", ["happy number", "subarray sum equals", "longest consecutive", "valid sudoku", "intersection of two arrays", "group anagrams", "two sum"]),
    ("Two Pointers", ["two pointers", "3sum", "4sum", "is subsequence", "remove duplicates", "container with most", "trapping rain", "valid palindrome"]),
    ("Arrays", ["array", "sum", "subarray", "duplicate", "zeroes", "rotate array", "product except", "majority", "pascal", "sort colors", "two sum", "3 sum", "container"]),
    ("Stack", ["valid parentheses", "simplify path", "daily temperatures", "decode string", "asteroid", "reverse polish", "evaluate reverse"]),
    ("Heap", ["kth largest", "top k", "find median", "last stone", "k closest", "reorganize"]),
]

# Short tokens that must match as whole words (avoid "bst" in climbStairs, "ll" in fill/AllRooms).
_WORD_BOUNDARY_KEYWORDS = {"bst", "lca"}


def _keyword_matches(haystack: str, keyword: str) -> bool:
    if keyword in _WORD_BOUNDARY_KEYWORDS:
        return re.search(rf"(?<![a-z0-9]){re.escape(keyword)}(?![a-z0-9])", haystack) is not None
    return keyword in haystack


def _infer_topic(title: str, slug: str, method_name: str | None) -> str:
    haystack = f"{title} {slug} {method_name or ''}".lower().replace("-", " ")
    for topic, keywords in _TOPIC_RULES:
        if any(_keyword_matches(haystack, kw) for kw in keywords):
            return topic
    return "Arrays"


def _load_existing_titles_from_company_problems() -> dict:
    """Parse existing inline metadata from CompanyProblems if present."""
    path = _REPO / "frontend" / "src" / "pages" / "CompanyProblems.jsx"
    if not path.is_file():
        return {}
    text = path.read_text(encoding="utf-8")
    # Keep hand-maintained entries by extracting title keys already in file
    return {}


def main() -> None:
    metadata: dict[str, dict] = {}

    for meta_path in sorted(_PROBLEMS.glob("*/meta.yaml")):
        raw = yaml.safe_load(meta_path.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            continue
        if raw.get("problem_type") == "cp":
            continue
        title = raw["title"]
        topic = _infer_topic(title, raw.get("slug", ""), raw.get("method_name"))
        companies = list(_DEFAULT_COMPANIES)

        # Prefer per-package sidecar written by scaffold (Blind75/NeetCode mappings)
        sidecar = meta_path.parent / ".codearena_meta.json"
        if sidecar.is_file():
            try:
                side = json.loads(sidecar.read_text(encoding="utf-8"))
                if isinstance(side.get("topic"), str) and side["topic"].strip():
                    topic = side["topic"].strip()
                if isinstance(side.get("companies"), list) and side["companies"]:
                    companies = [c for c in side["companies"] if isinstance(c, str)]
            except (json.JSONDecodeError, OSError):
                pass

        metadata[title] = {
            "topic": topic,
            "companies": companies,
        }

    _OUT.parent.mkdir(parents=True, exist_ok=True)
    body = (
        "// Auto-generated by backend/tools/generate_problem_metadata.py\n"
        "// Do not edit by hand — re-run the generator after adding problems.\n\n"
        f"export const DEFAULT_PROBLEM_COMPANIES = {json.dumps(_DEFAULT_COMPANIES, indent=4)};\n\n"
        f"export const PROBLEM_METADATA = {json.dumps(metadata, indent=4)};\n\n"
        "export function getProblemMetadata(title) {\n"
        "  if (!title) return null;\n"
        "  if (title === 'Spiral Matrix') return PROBLEM_METADATA[title] || null;\n"
        "  if (title.includes('Spiral') && title !== 'Spiral Matrix') title = 'Print the matrix in spiral manner';\n"
        "  return PROBLEM_METADATA[title] || null;\n"
        "}\n"
    )
    _OUT.write_text(body, encoding="utf-8")
    _BACKEND_OUT = _REPO / "backend" / "data" / "problem_metadata.json"
    _BACKEND_OUT.parent.mkdir(parents=True, exist_ok=True)
    _BACKEND_OUT.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(f"Wrote {len(metadata)} entries to {_OUT}")
    print(f"Wrote {len(metadata)} entries to {_BACKEND_OUT}")


if __name__ == "__main__":
    main()
