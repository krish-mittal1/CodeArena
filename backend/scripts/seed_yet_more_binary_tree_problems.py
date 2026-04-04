from __future__ import annotations

import asyncio
import random
from collections import deque

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.config import settings
from backend.core.constants import Difficulty
from backend.scripts.array_seed_utils import make_case, upsert_problem
from backend.scripts.seed_more_binary_tree_problems import (
    TARGET_CASES,
    TreeNode,
    build_tree,
    clone_tree,
    random_tree_array,
    tree_to_array,
)
from backend.scripts.seed_even_more_binary_tree_problems import random_unique_tree_array


def solve_lca_value(root: TreeNode | None, p: int, q: int) -> int:
    def dfs(node: TreeNode | None) -> TreeNode | None:
        if node is None:
            return None
        if node.val == p or node.val == q:
            return node
        left = dfs(node.left)
        right = dfs(node.right)
        if left and right:
            return node
        return left or right

    node = dfs(root)
    return node.val if node else -1


def solve_flatten(root: TreeNode | None) -> TreeNode | None:
    vals: list[int] = []

    def preorder(node: TreeNode | None) -> None:
        if node is None:
            return
        vals.append(node.val)
        preorder(node.left)
        preorder(node.right)

    preorder(root)
    if not vals:
        return None
    dummy = TreeNode(0)
    cur = dummy
    for value in vals:
        cur.right = TreeNode(value)
        cur = cur.right
    return dummy.right


def solve_path_sum_ii(root: TreeNode | None, target_sum: int) -> list[list[int]]:
    out: list[list[int]] = []

    def dfs(node: TreeNode | None, remaining: int, path: list[int]) -> None:
        if node is None:
            return
        path.append(node.val)
        remaining -= node.val
        if node.left is None and node.right is None and remaining == 0:
            out.append(path.copy())
        else:
            dfs(node.left, remaining, path)
            dfs(node.right, remaining, path)
        path.pop()

    dfs(root, target_sum, [])
    return out


def solve_sum_numbers(root: TreeNode | None) -> int:
    def dfs(node: TreeNode | None, current: int) -> int:
        if node is None:
            return 0
        current = current * 10 + node.val
        if node.left is None and node.right is None:
            return current
        return dfs(node.left, current) + dfs(node.right, current)

    return dfs(root, 0)


def solve_binary_tree_paths(root: TreeNode | None) -> list[str]:
    out: list[str] = []

    def dfs(node: TreeNode | None, path: list[str]) -> None:
        if node is None:
            return
        path.append(str(node.val))
        if node.left is None and node.right is None:
            out.append("->".join(path))
        else:
            dfs(node.left, path)
            dfs(node.right, path)
        path.pop()

    dfs(root, [])
    return out


def solve_count_nodes(root: TreeNode | None) -> int:
    if root is None:
        return 0
    return 1 + solve_count_nodes(root.left) + solve_count_nodes(root.right)


def solve_path_sum_iii(root: TreeNode | None, target_sum: int) -> int:
    prefix = {0: 1}

    def dfs(node: TreeNode | None, current: int) -> int:
        if node is None:
            return 0
        current += node.val
        total = prefix.get(current - target_sum, 0)
        prefix[current] = prefix.get(current, 0) + 1
        total += dfs(node.left, current)
        total += dfs(node.right, current)
        prefix[current] -= 1
        if prefix[current] == 0:
            del prefix[current]
        return total

    return dfs(root, 0)


def solve_sum_of_left_leaves(root: TreeNode | None) -> int:
    if root is None:
        return 0
    total = 0
    if root.left is not None and root.left.left is None and root.left.right is None:
        total += root.left.val
    return total + solve_sum_of_left_leaves(root.left) + solve_sum_of_left_leaves(root.right)


def solve_largest_values(root: TreeNode | None) -> list[int]:
    if root is None:
        return []
    out: list[int] = []
    queue: deque[TreeNode] = deque([root])
    while queue:
        level_max = -10**18
        for _ in range(len(queue)):
            node = queue.popleft()
            level_max = max(level_max, node.val)
            if node.left is not None:
                queue.append(node.left)
            if node.right is not None:
                queue.append(node.right)
        out.append(int(level_max))
    return out


def solve_is_complete_tree(root: TreeNode | None) -> bool:
    if root is None:
        return True
    queue: deque[TreeNode | None] = deque([root])
    seen_null = False
    while queue:
        node = queue.popleft()
        if node is None:
            seen_null = True
            continue
        if seen_null:
            return False
        queue.append(node.left)
        queue.append(node.right)
    return True


def choose_existing_values(root: TreeNode | None, rng: random.Random) -> tuple[int, int]:
    values: list[int] = []

    def dfs(node: TreeNode | None) -> None:
        if node is None:
            return
        values.append(node.val)
        dfs(node.left)
        dfs(node.right)

    dfs(root)
    if len(values) == 1:
        return values[0], values[0]
    p, q = rng.sample(values, 2)
    return p, q


def build_lca_cases() -> list[dict]:
    cases: list[dict] = []
    idx = 0
    samples = [
        ([3, 5, 1, 6, 2, 0, 8, None, None, 7, 4], 5, 1, 3),
        ([3, 5, 1, 6, 2, 0, 8, None, None, 7, 4], 5, 4, 5),
    ]
    for values, p, q, expected in samples:
        cases.append(make_case(values, p, q, expected_output=expected, idx=idx, is_sample=True))
        idx += 1

    rng = random.Random(2026040422)
    fixed_values = [
        [1, 2],
        [2, 1, 3],
        [4, 2, 6, 1, 3, 5, 7],
        [7, 3, 9, 1, 5, 8, 10, None, 2, 4, 6],
    ]
    for values in fixed_values:
        root = build_tree(values)
        p, q = choose_existing_values(root, rng)
        cases.append(make_case(values, p, q, expected_output=solve_lca_value(root, p, q), idx=idx))
        idx += 1

    while len(cases) < TARGET_CASES:
        values = random_unique_tree_array(rng, max_nodes=rng.randint(2, 180), allow_empty=False, value_low=-4000, value_high=4000)
        root = build_tree(values)
        p, q = choose_existing_values(root, rng)
        cases.append(make_case(values, p, q, expected_output=solve_lca_value(root, p, q), idx=idx))
        idx += 1
    return cases


def build_flatten_cases() -> list[dict]:
    cases: list[dict] = []
    idx = 0
    samples = [
        ([1, 2, 5, 3, 4, None, 6], [1, None, 2, None, 3, None, 4, None, 5, None, 6]),
        ([], []),
    ]
    for values, expected in samples:
        cases.append(make_case(values, expected_output=expected, idx=idx, is_sample=True))
        idx += 1

    fixed_values = [
        [0],
        [1, 2, 3],
        [1, None, 2, None, 3],
        [1, 2, None, 3, None, 4],
        [4, 2, 7, 1, 3, 6, 9],
    ]
    for values in fixed_values:
        cases.append(make_case(values, expected_output=tree_to_array(solve_flatten(build_tree(values))), idx=idx))
        idx += 1

    rng = random.Random(2026040423)
    while len(cases) < TARGET_CASES:
        values = random_tree_array(rng, max_nodes=rng.randint(0, 170), allow_empty=True, value_low=-200, value_high=200)
        cases.append(make_case(values, expected_output=tree_to_array(solve_flatten(build_tree(values))), idx=idx))
        idx += 1
    return cases


def build_path_sum_ii_cases() -> list[dict]:
    cases: list[dict] = []
    idx = 0
    samples = [
        ([5, 4, 8, 11, None, 13, 4, 7, 2, None, None, 5, 1], 22, [[5, 4, 11, 2], [5, 8, 4, 5]]),
        ([1, 2, 3], 5, []),
    ]
    for values, target, expected in samples:
        cases.append(make_case(values, target, expected_output=expected, idx=idx, is_sample=True))
        idx += 1

    rng = random.Random(2026040424)
    fixed = [
        ([1], 1),
        ([1], 2),
        ([1, 2], 3),
        ([-2, None, -3], -5),
        ([1, -2, -3, 1, 3, -2, None, -1], -1),
    ]
    for values, target in fixed:
        cases.append(make_case(values, target, expected_output=solve_path_sum_ii(build_tree(values), target), idx=idx))
        idx += 1

    while len(cases) < TARGET_CASES:
        values = random_tree_array(rng, max_nodes=rng.randint(1, 170), allow_empty=False, value_low=-20, value_high=20)
        root = build_tree(values)
        target = rng.randint(-80, 80)
        cases.append(make_case(values, target, expected_output=solve_path_sum_ii(root, target), idx=idx))
        idx += 1
    return cases


def build_sum_numbers_cases() -> list[dict]:
    cases: list[dict] = []
    idx = 0
    samples = [
        ([1, 2, 3], 25),
        ([4, 9, 0, 5, 1], 1026),
    ]
    for values, expected in samples:
        cases.append(make_case(values, expected_output=expected, idx=idx, is_sample=True))
        idx += 1

    rng = random.Random(2026040425)
    fixed_values = [
        [0],
        [1, 5, 1, None, None, None, 6],
        [9, 9, 9],
        [2, 1, 3, 0, None, None, 4],
    ]
    for values in fixed_values:
        cases.append(make_case(values, expected_output=solve_sum_numbers(build_tree(values)), idx=idx))
        idx += 1

    while len(cases) < TARGET_CASES:
        values = random_tree_array(rng, max_nodes=rng.randint(1, 120), allow_empty=False, value_low=0, value_high=9)
        cases.append(make_case(values, expected_output=solve_sum_numbers(build_tree(values)), idx=idx))
        idx += 1
    return cases


def build_binary_tree_paths_cases() -> list[dict]:
    cases: list[dict] = []
    idx = 0
    samples = [
        ([1, 2, 3, None, 5], ["1->2->5", "1->3"]),
        ([1], ["1"]),
    ]
    for values, expected in samples:
        cases.append(make_case(values, expected_output=expected, idx=idx, is_sample=True))
        idx += 1

    rng = random.Random(2026040426)
    fixed_values = [
        [],
        [1, 2, 3],
        [1, None, 2, None, 5],
        [1, 2, None, 3, None, 4],
    ]
    for values in fixed_values:
        cases.append(make_case(values, expected_output=solve_binary_tree_paths(build_tree(values)), idx=idx))
        idx += 1

    while len(cases) < TARGET_CASES:
        values = random_tree_array(rng, max_nodes=rng.randint(0, 160), allow_empty=True, value_low=-50, value_high=50)
        cases.append(make_case(values, expected_output=solve_binary_tree_paths(build_tree(values)), idx=idx))
        idx += 1
    return cases


def build_count_nodes_cases() -> list[dict]:
    cases: list[dict] = []
    idx = 0
    samples = [
        ([1, 2, 3, 4, 5, 6], 6),
        ([], 0),
    ]
    for values, expected in samples:
        cases.append(make_case(values, expected_output=expected, idx=idx, is_sample=True))
        idx += 1

    rng = random.Random(2026040427)
    fixed_values = [
        [1],
        [1, 2, 3],
        [1, 2, 3, 4, 5, 6, 7],
        [1, 2, 3, 4, 5, 6],
    ]
    for values in fixed_values:
        cases.append(make_case(values, expected_output=solve_count_nodes(build_tree(values)), idx=idx))
        idx += 1

    while len(cases) < TARGET_CASES:
        values = random_tree_array(rng, max_nodes=rng.randint(0, 220), allow_empty=True, value_low=-1000, value_high=1000)
        cases.append(make_case(values, expected_output=solve_count_nodes(build_tree(values)), idx=idx))
        idx += 1
    return cases


def build_path_sum_iii_cases() -> list[dict]:
    cases: list[dict] = []
    idx = 0
    samples = [
        ([10, 5, -3, 3, 2, None, 11, 3, -2, None, 1], 8, 3),
        ([5, 4, 8, 11, None, 13, 4, 7, 2, None, None, 5, 1], 22, 3),
    ]
    for values, target, expected in samples:
        cases.append(make_case(values, target, expected_output=expected, idx=idx, is_sample=True))
        idx += 1

    rng = random.Random(2026040428)
    fixed = [
        ([1], 1),
        ([1], 2),
        ([1, -1], 0),
        ([0, 1, 1], 1),
    ]
    for values, target in fixed:
        cases.append(make_case(values, target, expected_output=solve_path_sum_iii(build_tree(values), target), idx=idx))
        idx += 1

    while len(cases) < TARGET_CASES:
        values = random_tree_array(rng, max_nodes=rng.randint(1, 180), allow_empty=False, value_low=-20, value_high=20)
        target = rng.randint(-60, 60)
        cases.append(make_case(values, target, expected_output=solve_path_sum_iii(build_tree(values), target), idx=idx))
        idx += 1
    return cases


def build_sum_left_leaves_cases() -> list[dict]:
    cases: list[dict] = []
    idx = 0
    samples = [
        ([3, 9, 20, None, None, 15, 7], 24),
        ([1], 0),
    ]
    for values, expected in samples:
        cases.append(make_case(values, expected_output=expected, idx=idx, is_sample=True))
        idx += 1

    rng = random.Random(2026040429)
    fixed_values = [
        [1, 2, 3],
        [1, 2, None],
        [1, None, 2],
        [1, 2, 3, 4, 5],
    ]
    for values in fixed_values:
        cases.append(make_case(values, expected_output=solve_sum_of_left_leaves(build_tree(values)), idx=idx))
        idx += 1

    while len(cases) < TARGET_CASES:
        values = random_tree_array(rng, max_nodes=rng.randint(0, 180), allow_empty=True, value_low=-200, value_high=200)
        cases.append(make_case(values, expected_output=solve_sum_of_left_leaves(build_tree(values)), idx=idx))
        idx += 1
    return cases


def build_largest_values_cases() -> list[dict]:
    cases: list[dict] = []
    idx = 0
    samples = [
        ([1, 3, 2, 5, 3, None, 9], [1, 3, 9]),
        ([1, 2, 3], [1, 3]),
    ]
    for values, expected in samples:
        cases.append(make_case(values, expected_output=expected, idx=idx, is_sample=True))
        idx += 1

    rng = random.Random(2026040430)
    fixed_values = [
        [],
        [1],
        [-1, -2, -3],
        [5, 1, 9, 0, 4, 8, 10],
    ]
    for values in fixed_values:
        cases.append(make_case(values, expected_output=solve_largest_values(build_tree(values)), idx=idx))
        idx += 1

    while len(cases) < TARGET_CASES:
        values = random_tree_array(rng, max_nodes=rng.randint(0, 180), allow_empty=True, value_low=-500, value_high=500)
        cases.append(make_case(values, expected_output=solve_largest_values(build_tree(values)), idx=idx))
        idx += 1
    return cases


def build_complete_tree_cases() -> list[dict]:
    cases: list[dict] = []
    idx = 0
    samples = [
        ([1, 2, 3, 4, 5, 6], True),
        ([1, 2, 3, 4, 5, None, 7], False),
    ]
    for values, expected in samples:
        cases.append(make_case(values, expected_output=expected, idx=idx, is_sample=True))
        idx += 1

    rng = random.Random(2026040431)
    fixed_values = [
        [],
        [1],
        [1, 2],
        [1, 2, 3, 4, 5, 6, 7],
        [1, 2, 3, 4, 5, 6],
        [1, 2, 3, 4, None, 6, 7],
    ]
    for values in fixed_values:
        cases.append(make_case(values, expected_output=solve_is_complete_tree(build_tree(values)), idx=idx))
        idx += 1

    while len(cases) < TARGET_CASES:
        values = random_tree_array(rng, max_nodes=rng.randint(0, 200), allow_empty=True, value_low=-100, value_high=100)
        cases.append(make_case(values, expected_output=solve_is_complete_tree(build_tree(values)), idx=idx))
        idx += 1
    return cases


PROBLEMS = [
    (
        "Lowest Common Ancestor of a Binary Tree",
        build_lca_cases,
        dict(
            description="Given the root of a binary tree with unique node values and two values p and q that exist in the tree, return the value of their lowest common ancestor.",
            difficulty=Difficulty.MEDIUM,
            input_format="Line 1: JSON array root in level-order form using null for missing children\nLine 2: integer p\nLine 3: integer q",
            output_format="Single integer: the value of the lowest common ancestor",
            constraints="2 <= number of nodes <= 10^5\nAll Node.val values are unique\n-10^9 <= Node.val <= 10^9",
            method_name="lowestCommonAncestorValue",
            parameters=[{"name": "root", "type": "TreeNode"}, {"name": "p", "type": "int"}, {"name": "q", "type": "int"}],
            return_type="int",
            time_limit_ms=1800,
            memory_limit_mb=256,
            rating=1300,
            is_active=True,
        ),
    ),
    (
        "Flatten Binary Tree to Linked List",
        build_flatten_cases,
        dict(
            description="Given the root of a binary tree, flatten the tree into a linked-list-shaped tree using the same nodes in preorder traversal order. Return the flattened root.",
            difficulty=Difficulty.MEDIUM,
            input_format="Line 1: JSON array root in level-order form using null for missing children",
            output_format="JSON array of the flattened tree in level-order form using null for missing children",
            constraints="0 <= number of nodes <= 2000\n-100 <= Node.val <= 100",
            method_name="flattenTree",
            parameters=[{"name": "root", "type": "TreeNode"}],
            return_type="TreeNode",
            time_limit_ms=1800,
            memory_limit_mb=256,
            rating=1300,
            is_active=True,
        ),
    ),
    (
        "Path Sum II",
        build_path_sum_ii_cases,
        dict(
            description="Given the root of a binary tree and an integer targetSum, return all root-to-leaf paths where the sum of the node values equals targetSum.",
            difficulty=Difficulty.MEDIUM,
            input_format="Line 1: JSON array root in level-order form using null for missing children\nLine 2: integer targetSum",
            output_format="JSON matrix of all matching root-to-leaf paths",
            constraints="0 <= number of nodes <= 5000\n-1000 <= Node.val <= 1000\n-10^5 <= targetSum <= 10^5",
            method_name="pathSum",
            parameters=[{"name": "root", "type": "TreeNode"}, {"name": "targetSum", "type": "int"}],
            return_type="int[][]",
            time_limit_ms=1800,
            memory_limit_mb=256,
            rating=1250,
            is_active=True,
        ),
    ),
    (
        "Sum Root to Leaf Numbers",
        build_sum_numbers_cases,
        dict(
            description="You are given the root of a binary tree containing digits from 0 to 9 only. Each root-to-leaf path represents a number. Return the total sum of all root-to-leaf numbers.",
            difficulty=Difficulty.MEDIUM,
            input_format="Line 1: JSON array root in level-order form using null for missing children",
            output_format="Single integer: the sum of all root-to-leaf numbers",
            constraints="1 <= number of nodes <= 1000\n0 <= Node.val <= 9\nThe depth of the tree does not exceed 10",
            method_name="sumNumbers",
            parameters=[{"name": "root", "type": "TreeNode"}],
            return_type="int",
            time_limit_ms=1500,
            memory_limit_mb=256,
            rating=1200,
            is_active=True,
        ),
    ),
    (
        "Binary Tree Paths",
        build_binary_tree_paths_cases,
        dict(
            description="Given the root of a binary tree, return all root-to-leaf paths in any order. Each path should be formatted as node values joined by '->'.",
            difficulty=Difficulty.EASY,
            input_format="Line 1: JSON array root in level-order form using null for missing children",
            output_format="JSON array of path strings",
            constraints="0 <= number of nodes <= 100\n-100 <= Node.val <= 100",
            method_name="binaryTreePaths",
            parameters=[{"name": "root", "type": "TreeNode"}],
            return_type="str[]",
            time_limit_ms=1500,
            memory_limit_mb=256,
            rating=1000,
            is_active=True,
        ),
    ),
    (
        "Count Complete Tree Nodes",
        build_count_nodes_cases,
        dict(
            description="Given the root of a complete binary tree, return the number of nodes in the tree.",
            difficulty=Difficulty.MEDIUM,
            input_format="Line 1: JSON array root in level-order form using null for missing children",
            output_format="Single integer: the number of nodes in the tree",
            constraints="0 <= number of nodes <= 5 * 10^4\n-5 * 10^4 <= Node.val <= 5 * 10^4",
            method_name="countNodes",
            parameters=[{"name": "root", "type": "TreeNode"}],
            return_type="int",
            time_limit_ms=1500,
            memory_limit_mb=256,
            rating=1200,
            is_active=True,
        ),
    ),
    (
        "Path Sum III",
        build_path_sum_iii_cases,
        dict(
            description="Given the root of a binary tree and an integer targetSum, return the number of paths where the sum of the values along the path equals targetSum. The path does not need to start at the root or end at a leaf, but it must go downward.",
            difficulty=Difficulty.MEDIUM,
            input_format="Line 1: JSON array root in level-order form using null for missing children\nLine 2: integer targetSum",
            output_format="Single integer: the number of valid downward paths",
            constraints="0 <= number of nodes <= 1000\n-10^9 <= Node.val <= 10^9\n-1000 <= targetSum <= 1000",
            method_name="pathSumIII",
            parameters=[{"name": "root", "type": "TreeNode"}, {"name": "targetSum", "type": "int"}],
            return_type="int",
            time_limit_ms=1800,
            memory_limit_mb=256,
            rating=1350,
            is_active=True,
        ),
    ),
    (
        "Sum of Left Leaves",
        build_sum_left_leaves_cases,
        dict(
            description="Given the root of a binary tree, return the sum of all left leaf nodes.",
            difficulty=Difficulty.EASY,
            input_format="Line 1: JSON array root in level-order form using null for missing children",
            output_format="Single integer: the sum of all left leaves",
            constraints="0 <= number of nodes <= 1000\n-1000 <= Node.val <= 1000",
            method_name="sumOfLeftLeaves",
            parameters=[{"name": "root", "type": "TreeNode"}],
            return_type="int",
            time_limit_ms=1500,
            memory_limit_mb=256,
            rating=950,
            is_active=True,
        ),
    ),
    (
        "Find Largest Value in Each Tree Row",
        build_largest_values_cases,
        dict(
            description="Given the root of a binary tree, return an array containing the largest value in each level of the tree.",
            difficulty=Difficulty.MEDIUM,
            input_format="Line 1: JSON array root in level-order form using null for missing children",
            output_format="JSON array containing the largest value from each tree row",
            constraints="0 <= number of nodes <= 10^4\n-2^31 <= Node.val <= 2^31 - 1",
            method_name="largestValues",
            parameters=[{"name": "root", "type": "TreeNode"}],
            return_type="int[]",
            time_limit_ms=1500,
            memory_limit_mb=256,
            rating=1150,
            is_active=True,
        ),
    ),
    (
        "Check Completeness of a Binary Tree",
        build_complete_tree_cases,
        dict(
            description="Given the root of a binary tree, determine if it is a complete binary tree.",
            difficulty=Difficulty.MEDIUM,
            input_format="Line 1: JSON array root in level-order form using null for missing children",
            output_format="Boolean true/false",
            constraints="1 <= number of nodes <= 100\n1 <= Node.val <= 1000",
            method_name="isCompleteTree",
            parameters=[{"name": "root", "type": "TreeNode"}],
            return_type="bool",
            time_limit_ms=1500,
            memory_limit_mb=256,
            rating=1250,
            is_active=True,
        ),
    ),
]


async def seed() -> None:
    engine = create_async_engine(settings.database_url, echo=False)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as db:
        for title, build_cases, kwargs in PROBLEMS:
            await upsert_problem(db, title, kwargs, build_cases())
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
