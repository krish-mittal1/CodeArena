from __future__ import annotations

import asyncio
import random
from collections import deque
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.config import settings
from backend.core.constants import Difficulty
from backend.scripts.array_seed_utils import make_case, upsert_problem

TARGET_CASES = 540


@dataclass
class TreeNode:
    val: int
    left: TreeNode | None = None
    right: TreeNode | None = None


def build_tree(values: list[int | None]) -> TreeNode | None:
    if not values:
        return None
    nodes = [None if value is None else TreeNode(value) for value in values]
    child_idx = 1
    for node in nodes:
        if node is None:
            continue
        if child_idx < len(nodes):
            node.left = nodes[child_idx]
            child_idx += 1
        if child_idx < len(nodes):
            node.right = nodes[child_idx]
            child_idx += 1
    return nodes[0]


def tree_to_array(root: TreeNode | None) -> list[int | None]:
    if root is None:
        return []
    out: list[int | None] = []
    queue: deque[TreeNode | None] = deque([root])
    while queue:
        node = queue.popleft()
        if node is None:
            out.append(None)
            continue
        out.append(node.val)
        queue.append(node.left)
        queue.append(node.right)
    while out and out[-1] is None:
        out.pop()
    return out


def clone_tree(root: TreeNode | None) -> TreeNode | None:
    if root is None:
        return None
    return TreeNode(root.val, clone_tree(root.left), clone_tree(root.right))


def random_tree_array(
    rng: random.Random,
    *,
    max_nodes: int,
    allow_empty: bool = True,
    value_low: int = -100,
    value_high: int = 100,
    null_bias: float = 0.33,
) -> list[int | None]:
    if allow_empty and rng.random() < 0.08:
        return []
    values: list[int | None] = [rng.randint(value_low, value_high)]
    node_count = 1
    idx = 0
    while idx < len(values) and node_count < max_nodes:
        current = values[idx]
        idx += 1
        if current is None:
            continue
        for _ in range(2):
            if node_count >= max_nodes:
                break
            if rng.random() < null_bias:
                values.append(None)
            else:
                values.append(rng.randint(value_low, value_high))
                node_count += 1
    while values and values[-1] is None:
        values.pop()
    return values


def make_skewed(values: list[int], *, left: bool) -> list[int | None]:
    if not values:
        return []
    out: list[int | None] = [values[0]]
    for value in values[1:]:
        if left:
            out.extend([value, None])
        else:
            out.extend([None, value])
    while out and out[-1] is None:
        out.pop()
    return out


def bst_insert(root: TreeNode | None, value: int) -> TreeNode:
    if root is None:
        return TreeNode(value)
    if value < root.val:
        root.left = bst_insert(root.left, value)
    elif value > root.val:
        root.right = bst_insert(root.right, value)
    return root


def random_bst_array(rng: random.Random, *, size: int, low: int = -2000, high: int = 2000) -> list[int | None]:
    values = rng.sample(range(low, high + 1), size)
    root: TreeNode | None = None
    for value in values:
        root = bst_insert(root, value)
    return tree_to_array(root)


def solve_max_depth(root: TreeNode | None) -> int:
    if root is None:
        return 0
    return 1 + max(solve_max_depth(root.left), solve_max_depth(root.right))


def solve_same_tree(a: TreeNode | None, b: TreeNode | None) -> bool:
    if a is None or b is None:
        return a is b
    return a.val == b.val and solve_same_tree(a.left, b.left) and solve_same_tree(a.right, b.right)


def solve_invert_tree(root: TreeNode | None) -> TreeNode | None:
    if root is None:
        return None
    return TreeNode(root.val, solve_invert_tree(root.right), solve_invert_tree(root.left))


def solve_level_order(root: TreeNode | None) -> list[list[int]]:
    if root is None:
        return []
    out: list[list[int]] = []
    queue: deque[TreeNode] = deque([root])
    while queue:
        level: list[int] = []
        for _ in range(len(queue)):
            node = queue.popleft()
            level.append(node.val)
            if node.left is not None:
                queue.append(node.left)
            if node.right is not None:
                queue.append(node.right)
        out.append(level)
    return out


def solve_is_valid_bst(root: TreeNode | None) -> bool:
    def dfs(node: TreeNode | None, low: int | None, high: int | None) -> bool:
        if node is None:
            return True
        if low is not None and node.val <= low:
            return False
        if high is not None and node.val >= high:
            return False
        return dfs(node.left, low, node.val) and dfs(node.right, node.val, high)

    return dfs(root, None, None)


def solve_max_path_sum(root: TreeNode | None) -> int:
    best = -10**18

    def dfs(node: TreeNode | None) -> int:
        nonlocal best
        if node is None:
            return 0
        left = max(dfs(node.left), 0)
        right = max(dfs(node.right), 0)
        best = max(best, node.val + left + right)
        return node.val + max(left, right)

    dfs(root)
    return int(best)


def build_max_depth_cases() -> list[dict]:
    cases: list[dict] = []
    idx = 0
    samples = [
        ([3, 9, 20, None, None, 15, 7], 3),
        ([1, None, 2], 2),
    ]
    for values, expected in samples:
        cases.append(make_case(values, expected_output=expected, idx=idx, is_sample=True))
        idx += 1

    fixed = [
        ([], 0),
        ([1], 1),
        ([1, 2, 3, 4, 5, 6, 7], 3),
        (make_skewed([1, 2, 3, 4, 5], left=True), 5),
        (make_skewed([1, 2, 3, 4, 5, 6], left=False), 6),
        ([1, 2, None, 3, None, 4], 4),
        ([1, None, 2, None, 3, None, 4, None, 5], 5),
        ([0, -1, 1, -2, None, None, 2], 3),
        ([5, 4, 8, 11, None, 13, 4, 7, 2], 4),
        ([1, 2, 3, 4, None, None, None, 5], 4),
    ]
    for values, expected in fixed:
        cases.append(make_case(values, expected_output=expected, idx=idx))
        idx += 1

    rng = random.Random(2026040401)
    while len(cases) < TARGET_CASES:
        values = random_tree_array(rng, max_nodes=rng.randint(1, 220), value_low=-1000, value_high=1000)
        cases.append(make_case(values, expected_output=solve_max_depth(build_tree(values)), idx=idx))
        idx += 1
    return cases


def build_same_tree_cases() -> list[dict]:
    cases: list[dict] = []
    idx = 0
    samples = [
        ([1, 2, 3], [1, 2, 3], True),
        ([1, 2], [1, None, 2], False),
        ([1, 2, 1], [1, 1, 2], False),
    ]
    for a, b, expected in samples:
        cases.append(make_case(a, b, expected_output=expected, idx=idx, is_sample=True))
        idx += 1

    fixed = [
        ([], [], True),
        ([], [1], False),
        ([1], [1], True),
        ([1], [2], False),
        (make_skewed([1, 2, 3, 4], left=True), make_skewed([1, 2, 3, 4], left=True), True),
        (make_skewed([1, 2, 3, 4], left=True), make_skewed([1, 2, 3, 4], left=False), False),
        ([1, 2, 3, None, 4], [1, 2, 3, None, 4], True),
        ([1, 2, 3, None, 4], [1, 2, 3, 4], False),
        ([0, -1, 1], [0, -1, 1], True),
        ([0, -1, 1], [0, 1, -1], False),
    ]
    for a, b, expected in fixed:
        cases.append(make_case(a, b, expected_output=expected, idx=idx))
        idx += 1

    rng = random.Random(2026040402)
    while len(cases) < TARGET_CASES:
        base = random_tree_array(rng, max_nodes=rng.randint(0, 180), allow_empty=True, value_low=-200, value_high=200)
        if rng.random() < 0.5:
            other = list(base)
        else:
            other = list(base)
            if not other:
                other = [rng.randint(-5, 5)]
            else:
                non_null_positions = [i for i, value in enumerate(other) if value is not None]
                mutation = rng.choice(non_null_positions)
                if mutation != 0 and rng.random() < 0.35:
                    other[mutation] = None
                else:
                    other[mutation] = int(other[mutation]) + rng.choice([-7, -3, 3, 7])
                while other and other[-1] is None:
                    other.pop()
        cases.append(
            make_case(
                base,
                other,
                expected_output=solve_same_tree(build_tree(base), build_tree(other)),
                idx=idx,
            )
        )
        idx += 1
    return cases


def build_invert_tree_cases() -> list[dict]:
    cases: list[dict] = []
    idx = 0
    samples = [
        ([4, 2, 7, 1, 3, 6, 9], [4, 7, 2, 9, 6, 3, 1]),
        ([2, 1, 3], [2, 3, 1]),
    ]
    for values, expected in samples:
        cases.append(make_case(values, expected_output=expected, idx=idx, is_sample=True))
        idx += 1

    fixed_values = [
        [],
        [1],
        make_skewed([1, 2, 3, 4], left=True),
        make_skewed([1, 2, 3, 4], left=False),
        [1, 2, 3, 4, 5, 6, 7],
        [1, None, 2, 3, None, None, 4],
        [5, 1, 8, None, 3, 7, 9],
        [0, -10, 10, -20, None, 5, 20],
    ]
    for values in fixed_values:
        cases.append(
            make_case(values, expected_output=tree_to_array(solve_invert_tree(build_tree(values))), idx=idx)
        )
        idx += 1

    rng = random.Random(2026040403)
    while len(cases) < TARGET_CASES:
        values = random_tree_array(rng, max_nodes=rng.randint(0, 170), allow_empty=True, value_low=-500, value_high=500)
        cases.append(
            make_case(values, expected_output=tree_to_array(solve_invert_tree(build_tree(values))), idx=idx)
        )
        idx += 1
    return cases


def build_level_order_cases() -> list[dict]:
    cases: list[dict] = []
    idx = 0
    samples = [
        ([3, 9, 20, None, None, 15, 7], [[3], [9, 20], [15, 7]]),
        ([1], [[1]]),
        ([], []),
    ]
    for values, expected in samples:
        cases.append(make_case(values, expected_output=expected, idx=idx, is_sample=True))
        idx += 1

    fixed_values = [
        [1, 2, 3, 4, 5, 6, 7],
        make_skewed([1, 2, 3, 4, 5], left=True),
        make_skewed([1, 2, 3, 4, 5], left=False),
        [1, 2, None, 3, None, 4, None],
        [0, -1, 1, -2, -3, 2, 3],
        [5, 4, 8, 11, None, 13, 4, 7, 2, None, None, 5, 1],
        [1, None, 2, 3, 4, None, 5],
    ]
    for values in fixed_values:
        cases.append(make_case(values, expected_output=solve_level_order(build_tree(values)), idx=idx))
        idx += 1

    rng = random.Random(2026040404)
    while len(cases) < TARGET_CASES:
        values = random_tree_array(rng, max_nodes=rng.randint(0, 180), allow_empty=True, value_low=-300, value_high=300)
        cases.append(make_case(values, expected_output=solve_level_order(build_tree(values)), idx=idx))
        idx += 1
    return cases


def build_validate_bst_cases() -> list[dict]:
    cases: list[dict] = []
    idx = 0
    samples = [
        ([2, 1, 3], True),
        ([5, 1, 4, None, None, 3, 6], False),
    ]
    for values, expected in samples:
        cases.append(make_case(values, expected_output=expected, idx=idx, is_sample=True))
        idx += 1

    fixed = [
        ([], True),
        ([1], True),
        ([2, 2, 2], False),
        ([10, 5, 15, None, None, 6, 20], False),
        ([8, 3, 10, 1, 6, None, 14, None, None, 4, 7, 13], True),
        ([5, 4, 6, None, None, 3, 7], False),
        ([0, -3, 9, -10, None, 5], True),
        (make_skewed([1, 2, 3, 4, 5], left=False), True),
        (make_skewed([5, 4, 3, 2, 1], left=True), True),
        ([3, 1, 5, 0, 2, 4, 6], True),
    ]
    for values, expected in fixed:
        cases.append(make_case(values, expected_output=expected, idx=idx))
        idx += 1

    rng = random.Random(2026040405)
    while len(cases) < TARGET_CASES:
        if rng.random() < 0.55:
            values = random_bst_array(rng, size=rng.randint(1, 120))
        else:
            values = random_bst_array(rng, size=rng.randint(2, 120))
            if values:
                tree = build_tree(values)
                if tree and tree.left:
                    tree.left.val = tree.val + rng.randint(0, 6)
                elif tree and tree.right:
                    tree.right.val = tree.val - rng.randint(0, 6)
                else:
                    values = [2, 2]
                    tree = build_tree(values)
                values = tree_to_array(tree)
        cases.append(make_case(values, expected_output=solve_is_valid_bst(build_tree(values)), idx=idx))
        idx += 1
    return cases


def build_max_path_sum_cases() -> list[dict]:
    cases: list[dict] = []
    idx = 0
    samples = [
        ([1, 2, 3], 6),
        ([-10, 9, 20, None, None, 15, 7], 42),
    ]
    for values, expected in samples:
        cases.append(make_case(values, expected_output=expected, idx=idx, is_sample=True))
        idx += 1

    fixed = [
        ([1], 1),
        ([-3], -3),
        ([2, -1], 2),
        ([5, 4, 8, 11, None, 13, 4, 7, 2, None, None, 5, 1], 48),
        ([1, -2, -3, 1, 3, -2, None, -1], 3),
        (make_skewed([1, 2, 3, 4, 5], left=True), 15),
        (make_skewed([-1, -2, -3, -4], left=False), -1),
        ([9, 6, -3, None, None, -6, 2, None, None, 2, None, -6, -6, -6], 16),
        ([10, 2, 10, 20, 1, -25, None, None, None, None, None, 3, 4], 42),
    ]
    for values, expected in fixed:
        cases.append(make_case(values, expected_output=expected, idx=idx))
        idx += 1

    rng = random.Random(2026040406)
    while len(cases) < TARGET_CASES:
        values = random_tree_array(rng, max_nodes=rng.randint(1, 180), allow_empty=False, value_low=-1000, value_high=1000)
        cases.append(make_case(values, expected_output=solve_max_path_sum(build_tree(values)), idx=idx))
        idx += 1
    return cases


PROBLEMS = [
    (
        "Maximum Depth of Binary Tree",
        build_max_depth_cases,
        dict(
            description="Given the root of a binary tree, return its maximum depth. A binary tree's maximum depth is the number of nodes along the longest path from the root node down to the farthest leaf node.",
            difficulty=Difficulty.EASY,
            input_format="Line 1: JSON array root in level-order form using null for missing children",
            output_format="Single integer: the maximum depth of the binary tree",
            constraints="0 <= number of nodes <= 10^4\n-100 <= Node.val <= 100",
            method_name="maxDepth",
            parameters=[{"name": "root", "type": "TreeNode"}],
            return_type="int",
            time_limit_ms=1500,
            memory_limit_mb=256,
            rating=900,
            is_active=True,
        ),
    ),
    (
        "Same Tree",
        build_same_tree_cases,
        dict(
            description="Given the roots of two binary trees p and q, return true if they are the same tree. Two binary trees are the same if they are structurally identical and every corresponding node stores the same value.",
            difficulty=Difficulty.EASY,
            input_format="Line 1: JSON array p in level-order form\nLine 2: JSON array q in level-order form",
            output_format="Boolean true/false",
            constraints="0 <= number of nodes in each tree <= 100\n-10^4 <= Node.val <= 10^4",
            method_name="isSameTree",
            parameters=[{"name": "p", "type": "TreeNode"}, {"name": "q", "type": "TreeNode"}],
            return_type="bool",
            time_limit_ms=1500,
            memory_limit_mb=256,
            rating=950,
            is_active=True,
        ),
    ),
    (
        "Invert Binary Tree",
        build_invert_tree_cases,
        dict(
            description="Given the root of a binary tree, invert the tree and return its root.",
            difficulty=Difficulty.EASY,
            input_format="Line 1: JSON array root in level-order form using null for missing children",
            output_format="JSON array of the inverted tree in level-order form using null for missing children",
            constraints="0 <= number of nodes <= 100\n-100 <= Node.val <= 100",
            method_name="invertTree",
            parameters=[{"name": "root", "type": "TreeNode"}],
            return_type="TreeNode",
            time_limit_ms=1500,
            memory_limit_mb=256,
            rating=1000,
            is_active=True,
        ),
    ),
    (
        "Binary Tree Level Order Traversal",
        build_level_order_cases,
        dict(
            description="Given the root of a binary tree, return the level order traversal of its nodes' values from left to right, level by level.",
            difficulty=Difficulty.MEDIUM,
            input_format="Line 1: JSON array root in level-order form using null for missing children",
            output_format="JSON matrix representing the node values level by level",
            constraints="0 <= number of nodes <= 2000\n-1000 <= Node.val <= 1000",
            method_name="levelOrder",
            parameters=[{"name": "root", "type": "TreeNode"}],
            return_type="int[][]",
            time_limit_ms=1500,
            memory_limit_mb=256,
            rating=1150,
            is_active=True,
        ),
    ),
    (
        "Validate Binary Search Tree",
        build_validate_bst_cases,
        dict(
            description="Given the root of a binary tree, determine if it is a valid binary search tree. Every node in the left subtree must be smaller than the node, every node in the right subtree must be larger, and both subtrees must also be valid BSTs.",
            difficulty=Difficulty.MEDIUM,
            input_format="Line 1: JSON array root in level-order form using null for missing children",
            output_format="Boolean true/false",
            constraints="1 <= number of nodes <= 10^4\n-2^31 <= Node.val <= 2^31 - 1",
            method_name="isValidBST",
            parameters=[{"name": "root", "type": "TreeNode"}],
            return_type="bool",
            time_limit_ms=1800,
            memory_limit_mb=256,
            rating=1250,
            is_active=True,
        ),
    ),
    (
        "Binary Tree Maximum Path Sum",
        build_max_path_sum_cases,
        dict(
            description="A path in a binary tree is any sequence of nodes where adjacent nodes are connected by an edge. The path does not need to pass through the root. Return the maximum path sum of any non-empty path.",
            difficulty=Difficulty.HARD,
            input_format="Line 1: JSON array root in level-order form using null for missing children",
            output_format="Single integer: the maximum path sum",
            constraints="1 <= number of nodes <= 3 * 10^4\n-1000 <= Node.val <= 1000",
            method_name="maxPathSum",
            parameters=[{"name": "root", "type": "TreeNode"}],
            return_type="int",
            time_limit_ms=2000,
            memory_limit_mb=256,
            rating=1500,
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
