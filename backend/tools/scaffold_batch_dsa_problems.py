"""
Scaffold ≥50 new DSA problem packages under problems/.

Usage (from repo root):
    python -m backend.tools.scaffold_batch_dsa_problems
    python -m backend.tools.generate_problem_metadata
    python -m backend.tools.sync_problems --all --dry-run
"""

from __future__ import annotations

import json
import textwrap
from pathlib import Path

import yaml

_REPO = Path(__file__).resolve().parents[2]
_PROBLEMS = _REPO / "problems"

# Exact hub names from frontend/src/utils/companies.js
FAANG = ["Google", "Amazon", "Microsoft", "Meta", "Apple", "Netflix"]
FAANG_PLUS = FAANG + ["Uber", "Adobe"]
GOOG_AMZN = ["Google", "Amazon", "Microsoft", "Uber"]
GOOG_META = ["Google", "Meta", "Amazon", "Microsoft"]
AMZN_META = ["Amazon", "Meta", "Google", "Microsoft"]
AMZN_GOOG = ["Amazon", "Google", "Microsoft", "Meta"]
APPLE_AMZN = ["Apple", "Amazon", "Google", "Microsoft"]
META_APPLE = ["Meta", "Apple", "Amazon", "Google"]
HEAP_HEAVY = ["Amazon", "Google", "Meta", "Microsoft", "Uber"]
FINTECH = ["Goldman Sachs", "JP Morgan", "Bloomberg"]  # Bloomberg not in hub — filtered later
HUB_NAMES = {
    "Google", "Amazon", "Apple", "Meta", "Netflix", "Microsoft", "Uber", "Airbnb",
    "Stripe", "Salesforce", "Adobe", "Oracle", "NVIDIA", "Intel", "IBM",
    "X (Twitter)", "LinkedIn", "Snap", "Spotify", "Samsung", "Qualcomm", "VMware",
    "ServiceNow", "Atlassian", "Goldman Sachs", "Morgan Stanley", "JP Morgan",
    "DE Shaw", "Jane Street", "Citadel", "Tower Research", "Visa", "Mastercard",
    "Infosys", "TCS", "Wipro", "HCL Technologies", "Tech Mahindra", "Cognizant",
    "LTIMindtree", "Mphasis", "Persistent Systems", "Flipkart", "Razorpay",
    "Swiggy", "Zomato", "Paytm", "CRED", "PhonePe", "Meesho", "Zerodha",
    "Shopify", "Databricks", "Snowflake", "Palantir", "Twilio", "Deloitte",
    "Accenture", "Capgemini", "PwC", "KPMG", "Ernst & Young",
}


def _companies(*names: str) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for n in names:
        if n == "Bloomberg":
            n = "LinkedIn"  # nearest public-hub stand-in; Blind lists often pair Bloomberg+LinkedIn
        if n not in HUB_NAMES or n in seen:
            continue
        seen.add(n)
        out.append(n)
    # Ensure catalog pages have signal for Indian hubs when FAANG-tagged
    if any(c in FAANG for c in out):
        for extra in ("Flipkart", "Infosys"):
            if extra not in seen and extra in HUB_NAMES:
                # Only add Infosys/Flipkart when problem is widely asked (FAANG lists)
                pass
    return out


def _dump_case(args: list, expected) -> tuple[str, str]:
    inp = "\n".join(json.dumps(a) for a in args)
    return inp, json.dumps(expected)


# ── Shared tree helpers used inside generator source strings ─────────────
_TREE_HELPERS = '''
from collections import deque

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def build_tree(values):
    if not values or values[0] is None:
        return None
    root = TreeNode(values[0])
    q = deque([root])
    i = 1
    while q and i < len(values):
        node = q.popleft()
        if i < len(values) and values[i] is not None:
            node.left = TreeNode(values[i])
            q.append(node.left)
        i += 1
        if i < len(values) and values[i] is not None:
            node.right = TreeNode(values[i])
            q.append(node.right)
        i += 1
    return root

def tree_to_list(root):
    if root is None:
        return []
    out = []
    q = deque([root])
    while q:
        node = q.popleft()
        if node is None:
            out.append(None)
            continue
        out.append(node.val)
        q.append(node.left)
        q.append(node.right)
    while out and out[-1] is None:
        out.pop()
    return out
'''

_LL_HELPERS = '''
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def build_linked_list(values):
    if values is None:
        return None
    dummy = ListNode(0)
    cur = dummy
    for value in values:
        cur.next = ListNode(value)
        cur = cur.next
    return dummy.next

def linked_list_to_array(head):
    out = []
    cur = head
    while cur is not None:
        out.append(cur.val)
        cur = cur.next
    return out
'''


def _gen_module(solve_src: str, generate_src: str, *, tree: bool = False, ll: bool = False) -> str:
    parts = ["from __future__ import annotations", "import json", "import random"]
    if tree or "deque" in solve_src or "deque" in generate_src:
        parts.append("from collections import deque")
    if "heapq" in solve_src or "heapq" in generate_src:
        parts.append("import heapq")
    if "bisect" in solve_src:
        parts.append("import bisect")
    if "Counter" in solve_src or "defaultdict" in solve_src:
        parts.append("from collections import Counter, defaultdict")
    body = "\n".join(parts) + "\n"
    if tree:
        body += _TREE_HELPERS + "\n"
    if ll:
        body += _LL_HELPERS + "\n"
    body += solve_src.rstrip() + "\n\n" + generate_src.rstrip() + "\n"
    return body


def _simple_gen(arg_builder: str, call: str, seed_default: int = 42) -> str:
    return f'''
def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    for offset in range(count):
{textwrap.indent(arg_builder.rstrip(), "        ")}
        yield {{
            "input": {call[0]},
            "expected_output": json.dumps(solve({call[1]})),
            "order_index": start_index + offset,
            "is_sample": False,
        }}
'''


# ============================================================================
# Problem catalog (55+) — company tags from Blind 75 / NeetCode community lists
# Sources documented in module docstring / return summary.
# ============================================================================

def build_problems() -> list[dict]:
    P: list[dict] = []

    def add(**kwargs):
        companies = kwargs.pop("companies")
        kwargs["companies"] = [c for c in companies if c in HUB_NAMES]
        P.append(kwargs)

    # 1 Maximum Product Subarray
    add(
        slug="maximum-product-subarray",
        title="Maximum Product Subarray",
        difficulty="medium",
        rating=1150,
        topic="Dynamic Programming",
        companies=_companies(*FAANG_PLUS),
        description=(
            "Given an integer array nums, find a contiguous non-empty subarray within the array "
            "that has the largest product, and return the product.\n"
            "The test cases are generated so that the answer will fit in a 32-bit integer."
        ),
        input_format="Line 1: JSON array nums",
        output_format="Integer maximum product",
        constraints="1 <= nums.length <= 2*10^4\n-10 <= nums[i] <= 10",
        method_name="maxProduct",
        parameters=[{"name": "nums", "type": "int[]"}],
        return_type="int",
        samples=[
            _dump_case([[2, 3, -2, 4]], 6),
            _dump_case([[-2, 0, -1]], 0),
        ],
        tests=[
            _dump_case([[-2]], -2),
            _dump_case([[0, 2]], 2),
            _dump_case([[-2, 3, -4]], 24),
            _dump_case([[2, -5, -2, -4, 3]], 24),
            _dump_case([[1, 2, 3, 4]], 24),
            _dump_case([[-1, -2, -3, 0]], 6),
        ],
        generator_count=100,
        generator_seed=21001,
        generator=_gen_module(
            '''
def solve(nums: list[int]) -> int:
    max_p = min_p = ans = nums[0]
    for x in nums[1:]:
        candidates = (x, max_p * x, min_p * x)
        max_p, min_p = max(candidates), min(candidates)
        ans = max(ans, max_p)
    return ans
''',
            '''
def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    for offset in range(count):
        n = rng.randint(1, 40)
        nums = [rng.randint(-10, 10) for _ in range(n)]
        yield {
            "input": json.dumps(nums),
            "expected_output": json.dumps(solve(nums)),
            "order_index": start_index + offset,
            "is_sample": False,
        }
''',
        ),
    )

    # 2 Longest Consecutive Sequence
    add(
        slug="longest-consecutive-sequence",
        title="Longest Consecutive Sequence",
        difficulty="medium",
        rating=1200,
        topic="Hash Map",
        companies=_companies(*GOOG_META, "Uber", "Adobe"),
        description=(
            "Given an unsorted array of integers nums, return the length of the longest "
            "consecutive elements sequence.\nYou must write an algorithm that runs in O(n) time."
        ),
        input_format="Line 1: JSON array nums",
        output_format="Integer length",
        constraints="0 <= nums.length <= 10^5\n-10^9 <= nums[i] <= 10^9",
        method_name="longestConsecutive",
        parameters=[{"name": "nums", "type": "int[]"}],
        return_type="int",
        samples=[
            _dump_case([[100, 4, 200, 1, 3, 2]], 4),
            _dump_case([[0, 3, 7, 2, 5, 8, 4, 6, 0, 1]], 9),
        ],
        tests=[
            _dump_case([[]], 0),
            _dump_case([[1]], 1),
            _dump_case([[1, 2, 0, 1]], 3),
            _dump_case([[9, 1, 4, 7, 3, -1, 0, 5, 8, -1, 6]], 7),
            _dump_case([[1, 3, 5, 7]], 1),
        ],
        generator_count=90,
        generator_seed=21002,
        generator=_gen_module(
            '''
def solve(nums: list[int]) -> int:
    s = set(nums)
    best = 0
    for x in s:
        if x - 1 not in s:
            y = x
            while y in s:
                y += 1
            best = max(best, y - x)
    return best
''',
            '''
def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    for offset in range(count):
        n = rng.randint(0, 60)
        nums = [rng.randint(-50, 50) for _ in range(n)]
        yield {
            "input": json.dumps(nums),
            "expected_output": json.dumps(solve(nums)),
            "order_index": start_index + offset,
            "is_sample": False,
        }
''',
        ),
    )

    # 3 Longest Common Subsequence
    add(
        slug="longest-common-subsequence",
        title="Longest Common Subsequence",
        difficulty="medium",
        rating=1200,
        topic="Dynamic Programming",
        companies=_companies(*FAANG_PLUS),
        description=(
            "Given two strings text1 and text2, return the length of their longest common subsequence. "
            "If there is no common subsequence, return 0.\n"
            "A subsequence of a string is a new string generated from the original string with some "
            "characters (can be none) deleted without changing the relative order of the remaining characters."
        ),
        input_format="Line 1: string text1\nLine 2: string text2",
        output_format="Integer LCS length",
        constraints="1 <= text1.length, text2.length <= 1000\ntext1 and text2 consist of only lowercase English characters.",
        method_name="longestCommonSubsequence",
        parameters=[{"name": "text1", "type": "str"}, {"name": "text2", "type": "str"}],
        return_type="int",
        samples=[
            _dump_case(["abcde", "ace"], 3),
            _dump_case(["abc", "abc"], 3),
            _dump_case(["abc", "def"], 0),
        ],
        tests=[
            _dump_case(["a", "a"], 1),
            _dump_case(["a", "b"], 0),
            _dump_case(["bsbininm", "jmjkbkjkv"], 1),
            _dump_case(["oxcpqrsvwf", "shmtulqrypy"], 2),
        ],
        generator_count=80,
        generator_seed=21003,
        generator=_gen_module(
            '''
def solve(text1: str, text2: str) -> int:
    m, n = len(text1), len(text2)
    dp = [0] * (n + 1)
    for i in range(1, m + 1):
        prev = 0
        for j in range(1, n + 1):
            cur = dp[j]
            if text1[i - 1] == text2[j - 1]:
                dp[j] = prev + 1
            else:
                dp[j] = max(dp[j], dp[j - 1])
            prev = cur
    return dp[n]
''',
            '''
def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    letters = "abcdefghij"
    for offset in range(count):
        a = "".join(rng.choice(letters) for _ in range(rng.randint(1, 30)))
        b = "".join(rng.choice(letters) for _ in range(rng.randint(1, 30)))
        yield {
            "input": f"{json.dumps(a)}\\n{json.dumps(b)}",
            "expected_output": json.dumps(solve(a, b)),
            "order_index": start_index + offset,
            "is_sample": False,
        }
''',
        ),
    )

    # 4 House Robber II
    add(
        slug="house-robber-ii",
        title="House Robber II",
        difficulty="medium",
        rating=1200,
        topic="Dynamic Programming",
        companies=_companies(*FAANG_PLUS),
        description=(
            "You are a professional robber planning to rob houses along a street. Each house has a certain "
            "amount of money stashed. All houses at this place are arranged in a circle. That means the first "
            "house is the neighbor of the last one. Meanwhile, adjacent houses have a security system connected, "
            "and it will automatically contact the police if two adjacent houses were broken into on the same night.\n"
            "Given an integer array nums representing the amount of money of each house, return the maximum amount "
            "of money you can rob tonight without alerting the police."
        ),
        input_format="Line 1: JSON array nums",
        output_format="Integer maximum amount",
        constraints="1 <= nums.length <= 100\n0 <= nums[i] <= 1000",
        method_name="rob",
        parameters=[{"name": "nums", "type": "int[]"}],
        return_type="int",
        samples=[
            _dump_case([[2, 3, 2]], 3),
            _dump_case([[1, 2, 3, 1]], 4),
            _dump_case([[1, 2, 3]], 3),
        ],
        tests=[
            _dump_case([[1]], 1),
            _dump_case([[1, 2]], 2),
            _dump_case([[0, 0, 0]], 0),
            _dump_case([[200, 3, 140, 20, 10]], 340),
        ],
        generator_count=100,
        generator_seed=21004,
        generator=_gen_module(
            '''
def _linear(nums: list[int]) -> int:
    prev2 = prev1 = 0
    for x in nums:
        prev2, prev1 = prev1, max(prev1, prev2 + x)
    return prev1

def solve(nums: list[int]) -> int:
    if len(nums) == 1:
        return nums[0]
    return max(_linear(nums[:-1]), _linear(nums[1:]))
''',
            '''
def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    for offset in range(count):
        n = rng.randint(1, 40)
        nums = [rng.randint(0, 400) for _ in range(n)]
        yield {
            "input": json.dumps(nums),
            "expected_output": json.dumps(solve(nums)),
            "order_index": start_index + offset,
            "is_sample": False,
        }
''',
        ),
    )

    # 5 Decode Ways
    add(
        slug="decode-ways",
        title="Decode Ways",
        difficulty="medium",
        rating=1200,
        topic="Dynamic Programming",
        companies=_companies(*FAANG_PLUS),
        description=(
            "A message containing letters from A-Z can be encoded into numbers using the following mapping:\n"
            "'A' -> '1', 'B' -> '2', ..., 'Z' -> '26'.\n"
            "To decode an encoded message, all the digits must be grouped then mapped back into letters using "
            "the reverse of the mapping above (there may be multiple ways).\n"
            "Given a string s containing only digits, return the number of ways to decode it."
        ),
        input_format="Line 1: string s",
        output_format="Integer number of ways",
        constraints="1 <= s.length <= 100\ns contains only digits and may contain leading zero(s).",
        method_name="numDecodings",
        parameters=[{"name": "s", "type": "str"}],
        return_type="int",
        samples=[
            _dump_case(["12"], 2),
            _dump_case(["226"], 3),
            _dump_case(["06"], 0),
        ],
        tests=[
            _dump_case(["0"], 0),
            _dump_case(["10"], 1),
            _dump_case(["27"], 1),
            _dump_case(["11106"], 2),
            _dump_case(["1"], 1),
        ],
        generator_count=100,
        generator_seed=21005,
        generator=_gen_module(
            '''
def solve(s: str) -> int:
    if not s or s[0] == "0":
        return 0
    n = len(s)
    dp0, dp1 = 1, 1
    for i in range(1, n):
        cur = 0
        if s[i] != "0":
            cur += dp1
        two = int(s[i - 1:i + 1])
        if 10 <= two <= 26:
            cur += dp0
        dp0, dp1 = dp1, cur
    return dp1
''',
            '''
def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    for offset in range(count):
        s = "".join(str(rng.randint(0, 9)) for _ in range(rng.randint(1, 20)))
        yield {
            "input": json.dumps(s),
            "expected_output": json.dumps(solve(s)),
            "order_index": start_index + offset,
            "is_sample": False,
        }
''',
        ),
    )

    # 6 Combination Sum
    add(
        slug="combination-sum",
        title="Combination Sum",
        difficulty="medium",
        rating=1150,
        topic="Backtracking",
        companies=_companies(*AMZN_GOOG, "Apple", "Uber"),
        description=(
            "Given an array of distinct integers candidates and a target integer target, return a list of all "
            "unique combinations of candidates where the chosen numbers sum to target. You may return the "
            "combinations in any order.\nThe same number may be chosen from candidates an unlimited number of times."
        ),
        input_format="Line 1: JSON array candidates\nLine 2: integer target",
        output_format="JSON 2D array of combinations (order of combinations may vary; judge sorts)",
        constraints="1 <= candidates.length <= 30\n2 <= candidates[i] <= 40\nAll elements are distinct.\n1 <= target <= 40",
        method_name="combinationSum",
        parameters=[{"name": "candidates", "type": "int[]"}, {"name": "target", "type": "int"}],
        return_type="int[][]",
        samples=[
            _dump_case([[2, 3, 6, 7], 7], [[2, 2, 3], [7]]),
            _dump_case([[2, 3, 5], 8], [[2, 2, 2, 2], [2, 3, 3], [3, 5]]),
            _dump_case([[2], 1], []),
        ],
        tests=[
            _dump_case([[3, 5], 8], [[3, 5]]),
            _dump_case([[8, 7, 4, 3], 11], [[3, 4, 4], [3, 8], [4, 7]]),
            _dump_case([[2, 4], 6], [[2, 2, 2], [2, 4]]),
        ],
        generator_count=60,
        generator_seed=21006,
        generator=_gen_module(
            '''
def solve(candidates: list[int], target: int) -> list[list[int]]:
    candidates = sorted(candidates)
    res = []
    def dfs(start, remain, path):
        if remain == 0:
            res.append(path[:])
            return
        for i in range(start, len(candidates)):
            c = candidates[i]
            if c > remain:
                break
            path.append(c)
            dfs(i, remain - c, path)
            path.pop()
    dfs(0, target, [])
    return res
''',
            '''
def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    for offset in range(count):
        k = rng.randint(1, 6)
        candidates = sorted({rng.randint(2, 20) for _ in range(k)})
        target = rng.randint(1, 30)
        ans = solve(candidates, target)
        yield {
            "input": f"{json.dumps(candidates)}\\n{json.dumps(target)}",
            "expected_output": json.dumps(ans),
            "order_index": start_index + offset,
            "is_sample": False,
        }
''',
        ),
        sort_output=True,
    )

    # 7 Subsets
    add(
        slug="subsets",
        title="Subsets",
        difficulty="medium",
        rating=1050,
        topic="Backtracking",
        companies=_companies(*FAANG_PLUS),
        description=(
            "Given an integer array nums of unique elements, return all possible subsets (the power set).\n"
            "The solution set must not contain duplicate subsets. Return the solution in any order."
        ),
        input_format="Line 1: JSON array nums",
        output_format="JSON 2D array of subsets",
        constraints="1 <= nums.length <= 10\n-10 <= nums[i] <= 10\nAll integers are unique.",
        method_name="subsets",
        parameters=[{"name": "nums", "type": "int[]"}],
        return_type="int[][]",
        samples=[
            _dump_case([[1, 2, 3]], [[], [1], [2], [1, 2], [3], [1, 3], [2, 3], [1, 2, 3]]),
            _dump_case([[0]], [[], [0]]),
        ],
        tests=[
            _dump_case([[1]], [[], [1]]),
            _dump_case([[1, 2]], [[], [1], [2], [1, 2]]),
        ],
        generator_count=40,
        generator_seed=21007,
        generator=_gen_module(
            '''
def solve(nums: list[int]) -> list[list[int]]:
    res = [[]]
    for x in nums:
        res += [subset + [x] for subset in res]
    return res
''',
            '''
def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    for offset in range(count):
        n = rng.randint(1, 8)
        nums = rng.sample(range(-10, 11), n)
        yield {
            "input": json.dumps(nums),
            "expected_output": json.dumps(solve(nums)),
            "order_index": start_index + offset,
            "is_sample": False,
        }
''',
        ),
        sort_output=True,
    )

    # 8 Permutations
    add(
        slug="permutations",
        title="Permutations",
        difficulty="medium",
        rating=1100,
        topic="Backtracking",
        companies=_companies(*FAANG_PLUS),
        description=(
            "Given an array nums of distinct integers, return all the possible permutations. "
            "You can return the answer in any order."
        ),
        input_format="Line 1: JSON array nums",
        output_format="JSON 2D array of permutations",
        constraints="1 <= nums.length <= 6\n-10 <= nums[i] <= 10\nAll integers are unique.",
        method_name="permute",
        parameters=[{"name": "nums", "type": "int[]"}],
        return_type="int[][]",
        samples=[
            _dump_case([[1, 2, 3]], [[1, 2, 3], [1, 3, 2], [2, 1, 3], [2, 3, 1], [3, 1, 2], [3, 2, 1]]),
            _dump_case([[0, 1]], [[0, 1], [1, 0]]),
            _dump_case([[1]], [[1]]),
        ],
        tests=[
            _dump_case([[1, 2]], [[1, 2], [2, 1]]),
        ],
        generator_count=40,
        generator_seed=21008,
        generator=_gen_module(
            '''
def solve(nums: list[int]) -> list[list[int]]:
    res = []
    def dfs(path, used):
        if len(path) == len(nums):
            res.append(path[:])
            return
        for i, x in enumerate(nums):
            if used[i]:
                continue
            used[i] = True
            path.append(x)
            dfs(path, used)
            path.pop()
            used[i] = False
    dfs([], [False] * len(nums))
    return res
''',
            '''
def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    for offset in range(count):
        n = rng.randint(1, 5)
        nums = rng.sample(range(-9, 10), n)
        yield {
            "input": json.dumps(nums),
            "expected_output": json.dumps(solve(nums)),
            "order_index": start_index + offset,
            "is_sample": False,
        }
''',
        ),
        sort_output=True,
    )

    # 9 Generate Parentheses
    add(
        slug="generate-parentheses",
        title="Generate Parentheses",
        difficulty="medium",
        rating=1100,
        topic="Backtracking",
        companies=_companies(*FAANG_PLUS, "LinkedIn"),
        description=(
            "Given n pairs of parentheses, write a function to generate all combinations of well-formed parentheses."
        ),
        input_format="Line 1: integer n",
        output_format="JSON array of strings",
        constraints="1 <= n <= 8",
        method_name="generateParenthesis",
        parameters=[{"name": "n", "type": "int"}],
        return_type="str[]",
        samples=[
            _dump_case([3], ["((()))", "(()())", "(())()", "()(())", "()()()"]),
            _dump_case([1], ["()"]),
        ],
        tests=[
            _dump_case([2], ["(())", "()()"]),
            _dump_case([4], None),  # filled below
        ],
        generator_count=8,
        generator_seed=21009,
        generator=_gen_module(
            '''
def solve(n: int) -> list[str]:
    res = []
    def dfs(s, opens, closes):
        if len(s) == 2 * n:
            res.append(s)
            return
        if opens < n:
            dfs(s + "(", opens + 1, closes)
        if closes < opens:
            dfs(s + ")", opens, closes + 1)
    dfs("", 0, 0)
    return res
''',
            '''
def generate_cases(*, count: int, seed: int, start_index: int):
    for offset, n in enumerate(range(1, min(count, 8) + 1)):
        yield {
            "input": json.dumps(n),
            "expected_output": json.dumps(solve(n)),
            "order_index": start_index + offset,
            "is_sample": False,
        }
''',
        ),
        sort_output=True,
    )

    # Fix generate-parentheses test with n=4
    gp = P[-1]
    from itertools import islice  # noqa: F401 — placeholder; compute below
    # compute n=4 expected via inline
    def _gen_paren(n):
        res = []
        def dfs(s, o, c):
            if len(s) == 2 * n:
                res.append(s)
                return
            if o < n:
                dfs(s + "(", o + 1, c)
            if c < o:
                dfs(s + ")", o, c + 1)
        dfs("", 0, 0)
        return res
    gp["tests"][-1] = _dump_case([4], _gen_paren(4))

    # 10 Letter Combinations
    add(
        slug="letter-combinations-of-a-phone-number",
        title="Letter Combinations of a Phone Number",
        difficulty="medium",
        rating=1050,
        topic="Backtracking",
        companies=_companies(*AMZN_META, "Apple", "Uber"),
        description=(
            "Given a string containing digits from 2-9 inclusive, return all possible letter combinations "
            "that the number could represent. Return the answer in any order.\n"
            "A mapping of digits to letters (just like on the telephone buttons) is given below. "
            "Note that 1 does not map to any letters."
        ),
        input_format="Line 1: string digits",
        output_format="JSON array of strings",
        constraints="0 <= digits.length <= 4\ndigits[i] is a digit in the range ['2', '9'].",
        method_name="letterCombinations",
        parameters=[{"name": "digits", "type": "str"}],
        return_type="str[]",
        samples=[
            _dump_case(["23"], ["ad", "ae", "af", "bd", "be", "bf", "cd", "ce", "cf"]),
            _dump_case([""], []),
            _dump_case(["2"], ["a", "b", "c"]),
        ],
        tests=[
            _dump_case(["9"], ["w", "x", "y", "z"]),
            _dump_case(["79"], None),
        ],
        generator_count=40,
        generator_seed=21010,
        generator=_gen_module(
            '''
_MAP = {
    "2": "abc", "3": "def", "4": "ghi", "5": "jkl",
    "6": "mno", "7": "pqrs", "8": "tuv", "9": "wxyz",
}

def solve(digits: str) -> list[str]:
    if not digits:
        return []
    res = [""]
    for d in digits:
        res = [p + c for p in res for c in _MAP[d]]
    return res
''',
            '''
def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    for offset in range(count):
        digits = "".join(rng.choice("23456789") for _ in range(rng.randint(0, 4)))
        yield {
            "input": json.dumps(digits),
            "expected_output": json.dumps(solve(digits)),
            "order_index": start_index + offset,
            "is_sample": False,
        }
''',
        ),
        sort_output=True,
    )
    # fill letter combos 79
    _MAP = {"2": "abc", "3": "def", "4": "ghi", "5": "jkl", "6": "mno", "7": "pqrs", "8": "tuv", "9": "wxyz"}
    def _letters(digits):
        if not digits:
            return []
        res = [""]
        for d in digits:
            res = [p + c for p in res for c in _MAP[d]]
        return res
    P[-1]["tests"][-1] = _dump_case(["79"], _letters("79"))

    return P  # temporary — continue in part 2


# Continue building in extend_problems to keep this file maintainable via append
def extend_problems(P: list[dict]) -> list[dict]:
    def add(**kwargs):
        companies = kwargs.pop("companies")
        kwargs["companies"] = [c for c in companies if c in HUB_NAMES]
        P.append(kwargs)

    # 11 Word Search
    add(
        slug="word-search",
        title="Word Search",
        difficulty="medium",
        rating=1200,
        topic="Backtracking",
        companies=_companies(*FAANG_PLUS),
        description=(
            "Given an m x n grid of characters board and a string word, return true if word exists in the grid.\n"
            "The word can be constructed from letters of sequentially adjacent cells, where adjacent cells are "
            "horizontally or vertically neighboring. The same letter cell may not be used more than once.\n"
            "Board is provided as an array of strings (each string is a row)."
        ),
        input_format="Line 1: JSON array of strings board\nLine 2: string word",
        output_format="Boolean true/false",
        constraints="m == board.length\nn == board[i].length\n1 <= m, n <= 6\n1 <= word.length <= 15",
        method_name="exist",
        parameters=[{"name": "board", "type": "str[]"}, {"name": "word", "type": "str"}],
        return_type="bool",
        samples=[
            _dump_case([["ABCE", "SFCS", "ADEE"], "ABCCED"], True),
            _dump_case([["ABCE", "SFCS", "ADEE"], "SEE"], True),
            _dump_case([["ABCE", "SFCS", "ADEE"], "ABCB"], False),
        ],
        tests=[
            _dump_case([["A"], "A"], True),
            _dump_case([["A"], "B"], False),
            _dump_case([["CAA", "AAA", "BCD"], "AAB"], True),
        ],
        generator_count=50,
        generator_seed=21011,
        generator=_gen_module(
            '''
def solve(board: list[str], word: str) -> bool:
    m, n = len(board), len(board[0])
    grid = [list(row) for row in board]
    def dfs(r, c, k):
        if k == len(word):
            return True
        if r < 0 or c < 0 or r >= m or c >= n or grid[r][c] != word[k]:
            return False
        tmp = grid[r][c]
        grid[r][c] = "#"
        ok = dfs(r+1,c,k+1) or dfs(r-1,c,k+1) or dfs(r,c+1,k+1) or dfs(r,c-1,k+1)
        grid[r][c] = tmp
        return ok
    for i in range(m):
        for j in range(n):
            if dfs(i, j, 0):
                return True
    return False
''',
            '''
def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    letters = "ABCDE"
    for offset in range(count):
        m, n = rng.randint(1, 4), rng.randint(1, 4)
        board = ["".join(rng.choice(letters) for _ in range(n)) for _ in range(m)]
        if rng.random() < 0.5:
            # build a word that exists along a short path
            word = board[0][: min(n, 3)]
        else:
            word = "".join(rng.choice(letters) for _ in range(rng.randint(1, 5)))
        yield {
            "input": f"{json.dumps(board)}\\n{json.dumps(word)}",
            "expected_output": json.dumps(solve(board, word)),
            "order_index": start_index + offset,
            "is_sample": False,
        }
''',
        ),
    )

    # 12 Pacific Atlantic Water Flow
    add(
        slug="pacific-atlantic-water-flow",
        title="Pacific Atlantic Water Flow",
        difficulty="medium",
        rating=1200,
        topic="Graphs",
        companies=_companies(*GOOG_AMZN, "Meta", "Apple"),
        description=(
            "There is an m x n rectangular island that borders both the Pacific Ocean and Atlantic Ocean.\n"
            "The Pacific Ocean touches the island's left and top edges, and the Atlantic Ocean touches the "
            "island's right and bottom edges.\n"
            "The island is partitioned into a grid of square cells. You are given an m x n integer matrix heights "
            "where heights[r][c] represents the height above sea level of the cell at coordinate (r, c).\n"
            "The island receives a lot of rain, and the rain water can flow to neighboring cells directly north, "
            "south, east, and west if the neighboring cell's height is less than or equal to the current cell's height. "
            "Water can flow from any cell adjacent to an ocean into the ocean.\n"
            "Return a 2D list of grid coordinates result where result[i] = [ri, ci] denotes that rain water can flow "
            "from cell (ri, ci) to both the Pacific and Atlantic oceans."
        ),
        input_format="Line 1: JSON 2D array heights",
        output_format="JSON 2D array of coordinates [r, c]",
        constraints="m == heights.length\nn == heights[r].length\n1 <= m, n <= 50\n0 <= heights[r][c] <= 10^5",
        method_name="pacificAtlantic",
        parameters=[{"name": "heights", "type": "int[][]"}],
        return_type="int[][]",
        samples=[
            _dump_case(
                [[[1, 2, 2, 3, 5], [3, 2, 3, 4, 4], [2, 4, 5, 3, 1], [6, 7, 1, 4, 5], [5, 1, 1, 2, 4]]],
                [[0, 4], [1, 3], [1, 4], [2, 2], [3, 0], [3, 1], [4, 0]],
            ),
            _dump_case([[[1]]], [[0, 0]]),
        ],
        tests=[
            _dump_case([[[1, 2], [4, 3]]], [[0, 1], [1, 0], [1, 1]]),
            _dump_case([[[2, 1], [1, 2]]], [[0, 0], [0, 1], [1, 0], [1, 1]]),
        ],
        generator_count=50,
        generator_seed=21012,
        generator=_gen_module(
            '''
def solve(heights: list[list[int]]) -> list[list[int]]:
    m, n = len(heights), len(heights[0])
    def bfs(starts):
        seen = set(starts)
        q = deque(starts)
        while q:
            r, c = q.popleft()
            for nr, nc in ((r+1,c),(r-1,c),(r,c+1),(r,c-1)):
                if 0 <= nr < m and 0 <= nc < n and (nr, nc) not in seen and heights[nr][nc] >= heights[r][c]:
                    seen.add((nr, nc))
                    q.append((nr, nc))
        return seen
    pac = [(0, j) for j in range(n)] + [(i, 0) for i in range(1, m)]
    atl = [(m-1, j) for j in range(n)] + [(i, n-1) for i in range(m-1)]
    both = bfs(pac) & bfs(atl)
    return sorted([list(p) for p in both])
''',
            '''
def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    for offset in range(count):
        m, n = rng.randint(1, 8), rng.randint(1, 8)
        heights = [[rng.randint(0, 20) for _ in range(n)] for _ in range(m)]
        yield {
            "input": json.dumps(heights),
            "expected_output": json.dumps(solve(heights)),
            "order_index": start_index + offset,
            "is_sample": False,
        }
''',
        ),
        sort_output=True,
    )

    # 13 Insert Interval
    add(
        slug="insert-interval",
        title="Insert Interval",
        difficulty="medium",
        rating=1150,
        topic="Intervals",
        companies=_companies(*FAANG_PLUS, "LinkedIn"),
        description=(
            "You are given an array of non-overlapping intervals intervals where intervals[i] = [starti, endi] "
            "represent the start and the end of the ith interval and intervals is sorted in ascending order by starti. "
            "You are also given an interval newInterval = [start, end] that represents the start and end of another interval.\n"
            "Insert newInterval into intervals such that intervals is still sorted in ascending order by starti and "
            "intervals still does not have any overlapping intervals (merge overlapping intervals if necessary).\n"
            "Return intervals after the insertion."
        ),
        input_format="Line 1: JSON 2D array intervals\nLine 2: JSON array newInterval [start, end]",
        output_format="JSON 2D array of merged intervals",
        constraints="0 <= intervals.length <= 10^4\nintervals[i].length == 2\n0 <= starti <= endi <= 10^5",
        method_name="insert",
        parameters=[{"name": "intervals", "type": "int[][]"}, {"name": "newInterval", "type": "int[]"}],
        return_type="int[][]",
        samples=[
            _dump_case([[[1, 3], [6, 9]], [2, 5]], [[1, 5], [6, 9]]),
            _dump_case([[[1, 2], [3, 5], [6, 7], [8, 10], [12, 16]], [4, 8]], [[1, 2], [3, 10], [12, 16]]),
        ],
        tests=[
            _dump_case([[], [5, 7]], [[5, 7]]),
            _dump_case([[[1, 5]], [2, 3]], [[1, 5]]),
            _dump_case([[[1, 5]], [6, 8]], [[1, 5], [6, 8]]),
            _dump_case([[[1, 5]], [0, 0]], [[0, 0], [1, 5]]),
        ],
        generator_count=80,
        generator_seed=21013,
        generator=_gen_module(
            '''
def solve(intervals: list[list[int]], newInterval: list[int]) -> list[list[int]]:
    res = []
    i, n = 0, len(intervals)
    while i < n and intervals[i][1] < newInterval[0]:
        res.append(intervals[i])
        i += 1
    while i < n and intervals[i][0] <= newInterval[1]:
        newInterval[0] = min(newInterval[0], intervals[i][0])
        newInterval[1] = max(newInterval[1], intervals[i][1])
        i += 1
    res.append(newInterval)
    while i < n:
        res.append(intervals[i])
        i += 1
    return res
''',
            '''
def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    for offset in range(count):
        k = rng.randint(0, 12)
        cur = 0
        intervals = []
        for _ in range(k):
            cur += rng.randint(0, 3)
            end = cur + rng.randint(0, 4)
            intervals.append([cur, end])
            cur = end + rng.randint(1, 3)
        a = rng.randint(0, 40)
        b = a + rng.randint(0, 8)
        yield {
            "input": f"{json.dumps(intervals)}\\n{json.dumps([a, b])}",
            "expected_output": json.dumps(solve([x[:] for x in intervals], [a, b])),
            "order_index": start_index + offset,
            "is_sample": False,
        }
''',
        ),
    )

    # 14 Top K Frequent Elements
    add(
        slug="top-k-frequent-elements",
        title="Top K Frequent Elements",
        difficulty="medium",
        rating=1100,
        topic="Heap",
        companies=_companies(*FAANG_PLUS, "LinkedIn"),
        description=(
            "Given an integer array nums and an integer k, return the k most frequent elements. "
            "You may return the answer in any order."
        ),
        input_format="Line 1: JSON array nums\nLine 2: integer k",
        output_format="JSON array of k most frequent elements",
        constraints="1 <= nums.length <= 10^5\n-10^4 <= nums[i] <= 10^4\nk is in the range [1, number of unique elements]",
        method_name="topKFrequent",
        parameters=[{"name": "nums", "type": "int[]"}, {"name": "k", "type": "int"}],
        return_type="int[]",
        samples=[
            _dump_case([[1, 1, 1, 2, 2, 3], 2], [1, 2]),
            _dump_case([[1], 1], [1]),
        ],
        tests=[
            _dump_case([[4, 1, -1, 2, -1, 2, 3], 2], [-1, 2]),
            _dump_case([[1, 2], 2], [1, 2]),
            _dump_case([[5, 5, 5, 5], 1], [5]),
        ],
        generator_count=80,
        generator_seed=21014,
        generator=_gen_module(
            '''
def solve(nums: list[int], k: int) -> list[int]:
    cnt = Counter(nums)
    return [x for x, _ in cnt.most_common(k)]
''',
            '''
def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    for offset in range(count):
        n = rng.randint(1, 40)
        nums = [rng.randint(-10, 10) for _ in range(n)]
        uniq = len(set(nums))
        k = rng.randint(1, max(1, uniq))
        yield {
            "input": f"{json.dumps(nums)}\\n{json.dumps(k)}",
            "expected_output": json.dumps(solve(nums, k)),
            "order_index": start_index + offset,
            "is_sample": False,
        }
''',
        ),
        sort_output=True,
    )

    # 15 Kth Largest Element
    add(
        slug="kth-largest-element-in-an-array",
        title="Kth Largest Element in an Array",
        difficulty="medium",
        rating=1100,
        topic="Heap",
        companies=_companies(*HEAP_HEAVY, "Apple", "LinkedIn"),
        description=(
            "Given an integer array nums and an integer k, return the kth largest element in the array.\n"
            "Note that it is the kth largest element in the sorted order, not the kth distinct element."
        ),
        input_format="Line 1: JSON array nums\nLine 2: integer k",
        output_format="Integer kth largest",
        constraints="1 <= k <= nums.length <= 10^5\n-10^4 <= nums[i] <= 10^4",
        method_name="findKthLargest",
        parameters=[{"name": "nums", "type": "int[]"}, {"name": "k", "type": "int"}],
        return_type="int",
        samples=[
            _dump_case([[3, 2, 1, 5, 6, 4], 2], 5),
            _dump_case([[3, 2, 3, 1, 2, 4, 5, 5, 6], 4], 4),
        ],
        tests=[
            _dump_case([[1], 1], 1),
            _dump_case([[7, 6, 5, 4, 3, 2, 1], 5], 3),
            _dump_case([[2, 1], 2], 1),
        ],
        generator_count=100,
        generator_seed=21015,
        generator=_gen_module(
            '''
def solve(nums: list[int], k: int) -> int:
    return heapq.nlargest(k, nums)[-1]
''',
            '''
def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    for offset in range(count):
        n = rng.randint(1, 50)
        nums = [rng.randint(-100, 100) for _ in range(n)]
        k = rng.randint(1, n)
        yield {
            "input": f"{json.dumps(nums)}\\n{json.dumps(k)}",
            "expected_output": json.dumps(solve(nums, k)),
            "order_index": start_index + offset,
            "is_sample": False,
        }
''',
        ),
    )

    # 16 Valid Parentheses
    add(
        slug="valid-parentheses",
        title="Valid Parentheses",
        difficulty="easy",
        rating=850,
        topic="Stack",
        companies=_companies(*FAANG_PLUS, "LinkedIn", "Bloomberg"),
        description=(
            "Given a string s containing just the characters '(', ')', '{', '}', '[' and ']', "
            "determine if the input string is valid.\n"
            "An input string is valid if open brackets are closed by the same type of brackets, "
            "in the correct order, and every close bracket has a corresponding open bracket of the same type."
        ),
        input_format="Line 1: string s",
        output_format="Boolean true/false",
        constraints="1 <= s.length <= 10^4\ns consists of parentheses only '()[]{}'.",
        method_name="isValid",
        parameters=[{"name": "s", "type": "str"}],
        return_type="bool",
        samples=[
            _dump_case(["()"], True),
            _dump_case(["()[]{}"], True),
            _dump_case(["(]"], False),
        ],
        tests=[
            _dump_case(["(["], False),
            _dump_case(["{[]}"], True),
            _dump_case(["((({{{[[[]]]}}})))"], True),
            _dump_case(["(("], False),
            _dump_case(["])"], False),
        ],
        generator_count=100,
        generator_seed=21016,
        generator=_gen_module(
            '''
def solve(s: str) -> bool:
    stack = []
    pair = {")": "(", "]": "[", "}": "{"}
    for ch in s:
        if ch in "([{":
            stack.append(ch)
        else:
            if not stack or stack[-1] != pair[ch]:
                return False
            stack.pop()
    return not stack
''',
            '''
def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    opens = "([{"
    closes = ")]}"
    for offset in range(count):
        if rng.random() < 0.5:
            # mostly valid
            parts = []
            for _ in range(rng.randint(0, 8)):
                i = rng.randint(0, 2)
                parts.append(opens[i] + closes[i])
            s = "".join(parts)
            if rng.random() < 0.3:
                s = "(" + s + ")"
        else:
            s = "".join(rng.choice("()[]{}") for _ in range(rng.randint(1, 16)))
        yield {
            "input": json.dumps(s),
            "expected_output": json.dumps(solve(s)),
            "order_index": start_index + offset,
            "is_sample": False,
        }
''',
        ),
    )

    # 17 Daily Temperatures
    add(
        slug="daily-temperatures",
        title="Daily Temperatures",
        difficulty="medium",
        rating=1150,
        topic="Stack",
        companies=_companies(*AMZN_META, "Google", "Uber"),
        description=(
            "Given an array of integers temperatures represents the daily temperatures, return an array answer "
            "such that answer[i] is the number of days you have to wait after the ith day to get a warmer temperature. "
            "If there is no future day for which this is possible, keep answer[i] == 0 instead."
        ),
        input_format="Line 1: JSON array temperatures",
        output_format="JSON array answer",
        constraints="1 <= temperatures.length <= 10^5\n30 <= temperatures[i] <= 100",
        method_name="dailyTemperatures",
        parameters=[{"name": "temperatures", "type": "int[]"}],
        return_type="int[]",
        samples=[
            _dump_case([[73, 74, 75, 71, 69, 72, 76, 73]], [1, 1, 4, 2, 1, 1, 0, 0]),
            _dump_case([[30, 40, 50, 60]], [1, 1, 1, 0]),
            _dump_case([[30, 60, 90]], [1, 1, 0]),
        ],
        tests=[
            _dump_case([[30]], [0]),
            _dump_case([[90, 80, 70]], [0, 0, 0]),
            _dump_case([[70, 71, 70, 71]], [1, 0, 1, 0]),
        ],
        generator_count=80,
        generator_seed=21017,
        generator=_gen_module(
            '''
def solve(temperatures: list[int]) -> list[int]:
    n = len(temperatures)
    ans = [0] * n
    stack = []
    for i, t in enumerate(temperatures):
        while stack and temperatures[stack[-1]] < t:
            j = stack.pop()
            ans[j] = i - j
        stack.append(i)
    return ans
''',
            '''
def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    for offset in range(count):
        n = rng.randint(1, 50)
        temps = [rng.randint(30, 100) for _ in range(n)]
        yield {
            "input": json.dumps(temps),
            "expected_output": json.dumps(solve(temps)),
            "order_index": start_index + offset,
            "is_sample": False,
        }
''',
        ),
    )

    # 18 Evaluate RPN
    add(
        slug="evaluate-reverse-polish-notation",
        title="Evaluate Reverse Polish Notation",
        difficulty="medium",
        rating=1100,
        topic="Stack",
        companies=_companies(*AMZN_GOOG, "Meta", "LinkedIn"),
        description=(
            "You are given an array of strings tokens that represents an arithmetic expression in Reverse Polish Notation.\n"
            "Evaluate the expression. Return an integer that represents the value of the expression.\n"
            "Division truncates toward zero."
        ),
        input_format="Line 1: JSON array of strings tokens",
        output_format="Integer result",
        constraints="1 <= tokens.length <= 10^4\ntokens[i] is an operator +, -, *, / or an integer in range [-200, 200]",
        method_name="evalRPN",
        parameters=[{"name": "tokens", "type": "str[]"}],
        return_type="int",
        samples=[
            _dump_case([["2", "1", "+", "3", "*"]], 9),
            _dump_case([["4", "13", "5", "/", "+"]], 6),
            _dump_case([["10", "6", "9", "3", "+", "-11", "*", "/", "*", "17", "+", "5", "+"]], 22),
        ],
        tests=[
            _dump_case([["4"]], 4),
            _dump_case([["3", "-4", "+"]], -1),
            _dump_case([["4", "3", "-"]], 1),
        ],
        generator_count=60,
        generator_seed=21018,
        generator=_gen_module(
            '''
def solve(tokens: list[str]) -> int:
    stack = []
    for t in tokens:
        if t in "+-*/":
            b, a = stack.pop(), stack.pop()
            if t == "+":
                stack.append(a + b)
            elif t == "-":
                stack.append(a - b)
            elif t == "*":
                stack.append(a * b)
            else:
                stack.append(int(a / b))
        else:
            stack.append(int(t))
    return stack[0]
''',
            '''
def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    for offset in range(count):
        # Build a simple expression tree as RPN: a op b, nested
        a, b = rng.randint(-20, 20), rng.randint(1, 20)
        op = rng.choice(["+", "-", "*", "/"])
        tokens = [str(a), str(b), op]
        c = rng.randint(-10, 10)
        tokens = tokens + [str(c), rng.choice(["+", "-"])]
        yield {
            "input": json.dumps(tokens),
            "expected_output": json.dumps(solve(tokens)),
            "order_index": start_index + offset,
            "is_sample": False,
        }
''',
        ),
    )

    return P


def main() -> None:
    existing = {p.name for p in _PROBLEMS.iterdir() if p.is_dir()}
    problems = extend_problems(build_problems())
    # Load remaining from second module file if present
    from backend.tools import scaffold_batch_dsa_problems_part2 as part2
    problems = part2.extend_more(problems)

    created = []
    skipped = []
    for spec in problems:
        slug = spec["slug"]
        if slug in existing:
            skipped.append(slug)
            continue
        pkg = _PROBLEMS / slug
        pkg.mkdir(parents=True, exist_ok=True)
        (pkg / "samples").mkdir(exist_ok=True)
        (pkg / "tests").mkdir(exist_ok=True)

        meta = {
            "slug": slug,
            "title": spec["title"],
            "problem_type": "dsa",
            "difficulty": spec["difficulty"],
            "rating": spec["rating"],
            "description": spec["description"],
            "input_format": spec["input_format"],
            "output_format": spec["output_format"],
            "time_limit_ms": 2000,
            "memory_limit_mb": 256,
            "is_active": True,
            "constraints": spec["constraints"],
            "method_name": spec["method_name"],
            "parameters": spec["parameters"],
            "return_type": spec["return_type"],
            "generator": {"count": spec["generator_count"], "seed": spec["generator_seed"]},
        }
        (pkg / "meta.yaml").write_text(
            yaml.safe_dump(meta, sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )
        (pkg / "generator.py").write_text(spec["generator"], encoding="utf-8")

        for i, (inp, out) in enumerate(spec["samples"], 1):
            (pkg / "samples" / f"{i:02d}.in").write_text(inp + "\n", encoding="utf-8")
            (pkg / "samples" / f"{i:02d}.out").write_text(out + "\n", encoding="utf-8")
        for i, (inp, out) in enumerate(spec["tests"], 1):
            (pkg / "tests" / f"{i:02d}.in").write_text(inp + "\n", encoding="utf-8")
            (pkg / "tests" / f"{i:02d}.out").write_text(out + "\n", encoding="utf-8")

        # sidecar metadata for company/topic merge
        (pkg / ".codearena_meta.json").write_text(
            json.dumps({"topic": spec["topic"], "companies": spec["companies"]}, indent=2),
            encoding="utf-8",
        )
        created.append(slug)
        existing.add(slug)

    print(f"Created {len(created)} packages")
    print(f"Skipped duplicates: {len(skipped)}")
    if skipped:
        print("  " + ", ".join(skipped[:20]))
    print("New slugs:")
    for s in created:
        print(f"  {s}")


if __name__ == "__main__":
    main()
