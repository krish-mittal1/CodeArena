"""One-shot helper: append meta.yaml examples.explanations for high-traffic DSA problems.

Run: python -m backend.tools._inject_explanations
Safe to re-run: skips packages that already have explanation: in meta.yaml.
"""

from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2] / "problems"

# slug -> list of explanation strings (aligned with samples by index)
EXPLANATIONS: dict[str, list[str]] = {
    "best-time-to-buy-and-sell-stock": [
        "Buy on day 2 (price = 1) and sell on day 5 (price = 6), profit = 6 - 1 = 5.",
        "Prices only decrease, so no profitable transaction exists; return 0.",
        "Buy on day 1 (price = 2) and sell on day 2 (price = 4), profit = 2.",
    ],
    "container-with-most-water": [
        "The max area is between height 8 (index 1) and height 7 (index 8): min(8,7) * 7 = 49.",
        "Only two lines of height 1; area = 1 * 1 = 1.",
    ],
    "maximum-subarray": [
        "The subarray [4,-1,2,1] has the largest sum 6.",
        "Single-element array; the answer is 1.",
        "The entire array is the maximum subarray with sum 23.",
    ],
    "product-of-array-except-self": [
        "For each index i, answer[i] is the product of all nums[j] where j != i.",
        "Zeros force most products to 0; only the positions that exclude the single zero stay non-zero.",
        "Both elements are zero, so every product-except-self is zero.",
    ],
    "trapping-rain-water": [
        "Water is trapped in the valleys between bars; total units trapped = 6.",
        "Water trapped between the bars sums to 9.",
    ],
    "house-robber": [
        "Rob house 1 (1) and house 3 (3) for a total of 4.",
        "Rob house 1 (2), house 3 (9), and house 5 (1) for a total of 12.",
    ],
    "unique-paths": [
        "A 3x7 grid has 28 unique paths from top-left to bottom-right moving only right or down.",
        "A 3x2 grid has 3 unique paths.",
    ],
    "word-break": [
        'Return true because "leetcode" can be segmented as "leet code".',
        'Return true because "applepenapple" can be segmented as "apple pen apple".',
        'Return false because "catsandog" cannot be segmented using the dictionary.',
    ],
    "number-of-islands": [
        "All land cells are connected into a single island, so the answer is 1.",
        "There are three islands: the top-left 2x2 block, the single cell in the middle, and the bottom-right 1x2 block.",
    ],
    "course-schedule": [
        "Take course 1 after course 0; there is no cycle, so it is possible.",
        "Courses 0 and 1 depend on each other, forming a cycle; return false.",
    ],
    "rotting-oranges": [
        "All fresh oranges become rotten in 4 minutes via BFS from initially rotten cells.",
        "A fresh orange is unreachable from any rotten orange, so return -1.",
        "No fresh oranges remain; return 0.",
    ],
    "valid-parentheses": [
        "The string contains a matching pair of parentheses.",
        "Every opening bracket has a corresponding closing bracket of the same type in the correct order.",
        "A closing bracket does not match the most recent unmatched opening bracket.",
    ],
    "group-anagrams": [
        'Group words by sorted letter signature: "eat"/"tea"/"ate", "tan"/"nat", and "bat".',
        "A single empty string forms one group.",
        'A single character forms one group.',
    ],
    "merge-intervals": [
        "Intervals [1,3] and [2,6] overlap and merge into [1,6]; the rest stay separate.",
        "Intervals [1,4] and [4,5] touch at 4 and merge into [1,5].",
        "Intervals [1,4] and [0,4] overlap and merge into [0,4].",
    ],
    "reverse-linked-list": [
        "Reversing 1→2→3→4→5 yields 5→4→3→2→1.",
        "Reversing 1→2 yields 2→1.",
        "An empty list reverses to an empty list.",
    ],
    "binary-tree-level-order-traversal": [
        "Level order visits nodes level by level: [[3],[9,20],[15,7]].",
        "A single-node tree has one level: [[1]].",
        "An empty tree has no levels.",
    ],
    "search-in-rotated-sorted-array": [
        "After rotation, target 0 is found at index 4.",
        "Target 3 is not present in the array, so return -1.",
    ],
    "longest-increasing-subsequence": [
        "One LIS is [2,3,7,101] with length 4.",
        "One LIS is [0,1,2,3] with length 4.",
        "All values are equal, so the LIS length is 1.",
    ],
    "pacific-atlantic-water-flow": [
        "Cells listed can flow downhill (or equal height) to both the Pacific (top/left) and Atlantic (bottom/right).",
        "A single cell borders both oceans, so [[0,0]] is returned.",
    ],
    "network-delay-time": [
        "From node 2, the farthest reachable node takes time 2.",
        "The signal reaches node 2 from 1 in time 1.",
        "Starting at node 2 cannot reach node 1, so return -1.",
    ],
    "edit-distance": [
        'horse → ros needs 3 operations (replace h→r, remove r, remove e).',
        "intention → execution needs 5 operations.",
    ],
    "decode-ways": [
        '"12" can be decoded as "AB" (1 2) or "L" (12) — 2 ways.',
        '"226" can be decoded as "BZ" (2 26), "VF" (22 6), or "BBF" (2 2 6) — 3 ways.',
        '"06" is invalid because it has a leading zero; return 0.',
    ],
    "partition-equal-subset-sum": [
        "The array sums to 22 and can be partitioned into [1,5,5] and [11].",
        "The array sums to 11 (odd), so equal partition is impossible.",
    ],
    "longest-common-subsequence": [
        'The LCS of "abcde" and "ace" is "ace" with length 3.',
        'The strings are identical, so LCS length is 3.',
        "The strings share no characters; LCS length is 0.",
    ],
    "top-k-frequent-elements": [
        "1 appears three times and 2 appears twice — the top 2 frequencies.",
        "Only one element exists; return it.",
    ],
    "valid-anagram": [
        '"anagram" and "nagaram" use the same multiset of letters.',
        '"rat" and "car" differ in letter counts.',
        "Two empty strings are anagrams.",
    ],
    "minimum-window-substring": [
        'The minimum window in s covering all of t = "ABC" is "BANC".',
        's and t are both "a", so the window is "a".',
    ],
    "diameter-of-binary-tree": [
        "The longest path is 4→2→1→3 or 5→2→1→3 with length 3 (edges).",
        "The path 2→1 has length 1.",
    ],
    "validate-binary-search-tree": [
        "Left < root < right holds for every subtree; it is a valid BST.",
        "Node 4 has left child 3, but 4 is on the right of 5, violating the BST range.",
    ],
    "merge-two-sorted-lists": [
        "Merge the two sorted lists into one sorted list.",
        "Both lists empty yields an empty list.",
        "Merging empty with [0] yields [0].",
    ],
    "move-zeroes": [
        "Non-zero elements keep relative order and move forward; zeros fill the end.",
        "A single zero stays in place.",
    ],
    "contains-duplicate": [
        "Value 1 appears twice, so return true.",
        "All values are unique, so return false.",
    ],
    "jump-game": [
        "From index 0 you can reach the last index (e.g. 0→1→4).",
        "You get stuck at index 3 (value 0) and cannot reach the end.",
    ],
    "coin-change-ii": [
        "There are 4 combinations that sum to 5: (1+1+1+1+1), (1+1+1+2), (1+2+2), (5).",
        "No combination of coins sums to 3 using only 2s.",
        "One way: a single coin of value 10.",
    ],
    "is-graph-bipartite": [
        "Odd cycles exist (e.g. 0-1-2), so the graph is not bipartite.",
        "The graph is a cycle of even length and can be 2-colored.",
    ],
    "surrounded-regions": [
        "Interior 'O's surrounded by 'X' are flipped; border-connected 'O's stay.",
        "A single 'X' board is unchanged.",
    ],
    "word-search": [
        'The word "ABCCED" exists along a contiguous path on the board.',
        'The word "SEE" exists on the board.',
        'The word "ABCB" cannot be formed without reusing a cell.',
    ],
    "daily-temperatures": [
        "For each day, wait until a warmer temperature; 0 means none exists later.",
        "Temperatures strictly increase until the last day.",
        "Each day (except the last) has a warmer day the next day.",
    ],
    "sliding-window-maximum": [
        "For each window of size 3, record the maximum value in that window.",
        "A window covering the single element returns that element.",
    ],
    "maximum-depth-of-binary-tree": [
        "The longest root-to-leaf path has 3 nodes, so depth is 3.",
        "Root → right child forms a path of depth 2.",
    ],
    "lowest-common-ancestor-of-a-binary-tree": [
        "Nodes 5 and 1 have LCA 3 (the root).",
        "Nodes 5 and 4 have LCA 5 (one node is an ancestor of the other).",
    ],
    "subsets": [
        "All subsets of [1,2,3] are listed (order among subsets may vary).",
        "A single-element set has the empty set and itself.",
    ],
    "permutations": [
        "All 6 permutations of [1,2,3] are returned (any order of the list is fine).",
        "All permutations of [0,1].",
        "A single element has one permutation.",
    ],
    "combination-sum": [
        "Combinations that sum to 7: [2,2,3] and [7] (reuse allowed).",
        "Combinations that sum to 8 using [2,3,5].",
        "No combination of 2s sums to 1; return an empty list.",
    ],
    "generate-parentheses": [
        "All valid parentheses strings with n = 3 pairs.",
        'For n = 1 the only string is "()".',
    ],
    "letter-combinations-of-a-phone-number": [
        'Digits "23" map to letter combinations of abc × def.',
        "An empty digits string yields no combinations.",
        'Digit "2" maps to ["a","b","c"].',
    ],
    "median-of-two-sorted-arrays": [
        "Merged sorted array is [1,2,3]; median is 2.",
        "Merged sorted array is [1,2,3,4]; median is (2+3)/2 = 2.5.",
    ],
    "kth-largest-element-in-an-array": [
        "The 2nd largest element in the array is 5.",
        "The 4th largest element is 4.",
    ],
    "longest-palindromic-substring": [
        '"bab" is a longest palindromic substring of "babad" ("aba" is also valid).',
        '"bb" is the longest palindromic substring of "cbbd".',
        'A single character is a palindrome of length 1.',
    ],
    "palindromic-substrings": [
        'Three palindromic substrings: "a", "b", "c".',
        'Six palindromic substrings in "aaa" (three singles, two doubles, one triple).',
        'Six palindromic substrings in "abba".',
    ],
    "flood-fill": [
        "Starting at (1,1), all 4-connected cells with the old color are recolored to 2.",
        "The starting pixel already has the new color; the image is unchanged.",
    ],
    "max-area-of-island": [
        "The largest island (4-connected land cells) has area 6.",
        "There is no land; return 0.",
    ],
    "keys-and-rooms": [
        "Starting from room 0 you can visit every room via collected keys.",
        "Room 2 is unreachable from room 0; return false.",
    ],
    "number-of-provinces": [
        "Cities 0–1 are connected and city 2 is alone — 2 provinces.",
        "Three isolated cities — 3 provinces.",
    ],
    "set-matrix-zeroes": [
        "Cell (1,1) is 0, so row 1 and column 1 become all zeros.",
        "Zeros at (0,0) and (0,3) zero out the first row and columns 0 and 3.",
        "A single non-zero cell is unchanged.",
    ],
    "spiral-matrix": [
        "Traverse clockwise from the top-left: 1→2→3→6→9→8→7→4→5.",
        "Spiral order of the 3×4 matrix.",
    ],
    "rotate-image": [
        "Rotate 90° clockwise: first row becomes last column.",
        "Rotate the 4×4 matrix 90° clockwise in place.",
    ],
    "game-of-life": [
        "Apply Conway Game of Life rules to every cell simultaneously.",
        "After one step, all four cells are live.",
        "A lone live cell dies from under-population.",
    ],
}


def _sample_count(slug: str) -> int:
    samples = ROOT / slug / "samples"
    if not samples.is_dir():
        return 0
    return len(list(samples.glob("*.in"))) + len(list(samples.glob("*.json")))


def inject(slug: str, explanations: list[str]) -> bool:
    meta_path = ROOT / slug / "meta.yaml"
    if not meta_path.is_file():
        print(f"skip missing: {slug}")
        return False
    text = meta_path.read_text(encoding="utf-8")
    if "explanation:" in text:
        print(f"skip existing: {slug}")
        return False
    n = _sample_count(slug)
    if n == 0 or not explanations:
        print(f"skip empty: {slug}")
        return False
    trimmed = explanations[:n]
    while len(trimmed) < n:
        trimmed.append("See the input and output for this sample.")
    data = yaml.safe_load(text)
    data["examples"] = [{"explanation": e.strip()} for e in trimmed]
    # Prefer block-style dump for readability
    dumped = yaml.safe_dump(
        data,
        sort_keys=False,
        allow_unicode=True,
        default_flow_style=False,
        width=100,
    )
    meta_path.write_text(dumped, encoding="utf-8")
    print(f"updated: {slug} ({len(trimmed)} explanations)")
    return True


def main() -> None:
    updated = 0
    for slug, exps in EXPLANATIONS.items():
        if inject(slug, exps):
            updated += 1
    print(f"\nDone. Updated {updated} packages.")


if __name__ == "__main__":
    main()
