from __future__ import annotations

import asyncio
import random

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.config import settings
from backend.core.constants import Difficulty
from backend.scripts.array_seed_utils import make_case, upsert_problem
from backend.scripts.seed_more_binary_tree_problems import (
    TARGET_CASES,
    TreeNode,
    build_tree,
    clone_tree,
    make_skewed,
    random_bst_array,
    random_tree_array,
    tree_to_array,
)


def random_unique_tree_array(
    rng: random.Random,
    *,
    max_nodes: int,
    allow_empty: bool = True,
    value_low: int = -1000,
    value_high: int = 1000,
) -> list[int | None]:
    template = random_tree_array(
        rng,
        max_nodes=max_nodes,
        allow_empty=allow_empty,
        value_low=0,
        value_high=0,
    )
    count = sum(value is not None for value in template)
    if count == 0:
        return []
    values = iter(rng.sample(range(value_low, value_high + 1), count))
    out = [next(values) if value is not None else None for value in template]
    while out and out[-1] is None:
        out.pop()
    return out


def preorder_values(root: TreeNode | None) -> list[int]:
    if root is None:
        return []
    return [root.val] + preorder_values(root.left) + preorder_values(root.right)


def inorder_values(root: TreeNode | None) -> list[int]:
    if root is None:
        return []
    return inorder_values(root.left) + [root.val] + inorder_values(root.right)


def solve_is_balanced(root: TreeNode | None) -> bool:
    def dfs(node: TreeNode | None) -> int:
        if node is None:
            return 0
        left = dfs(node.left)
        if left == -1:
            return -1
        right = dfs(node.right)
        if right == -1:
            return -1
        if abs(left - right) > 1:
            return -1
        return 1 + max(left, right)

    return dfs(root) != -1


def solve_diameter(root: TreeNode | None) -> int:
    best = 0

    def dfs(node: TreeNode | None) -> int:
        nonlocal best
        if node is None:
            return 0
        left = dfs(node.left)
        right = dfs(node.right)
        best = max(best, left + right)
        return 1 + max(left, right)

    dfs(root)
    return best


def solve_has_path_sum(root: TreeNode | None, target_sum: int) -> bool:
    if root is None:
        return False
    if root.left is None and root.right is None:
        return root.val == target_sum
    remaining = target_sum - root.val
    return solve_has_path_sum(root.left, remaining) or solve_has_path_sum(root.right, remaining)


def solve_symmetric(root: TreeNode | None) -> bool:
    def mirror(a: TreeNode | None, b: TreeNode | None) -> bool:
        if a is None or b is None:
            return a is b
        return a.val == b.val and mirror(a.left, b.right) and mirror(a.right, b.left)

    return mirror(root.left, root.right) if root else True


def solve_min_depth(root: TreeNode | None) -> int:
    if root is None:
        return 0
    if root.left is None and root.right is None:
        return 1
    if root.left is None:
        return 1 + solve_min_depth(root.right)
    if root.right is None:
        return 1 + solve_min_depth(root.left)
    return 1 + min(solve_min_depth(root.left), solve_min_depth(root.right))


def solve_right_side_view(root: TreeNode | None) -> list[int]:
    if root is None:
        return []
    queue = [root]
    out: list[int] = []
    while queue:
        out.append(queue[-1].val)
        next_level: list[TreeNode] = []
        for node in queue:
            if node.left is not None:
                next_level.append(node.left)
            if node.right is not None:
                next_level.append(node.right)
        queue = next_level
    return out


def solve_zigzag(root: TreeNode | None) -> list[list[int]]:
    if root is None:
        return []
    queue = [root]
    out: list[list[int]] = []
    left_to_right = True
    while queue:
        level = [node.val for node in queue]
        if not left_to_right:
            level.reverse()
        out.append(level)
        next_level: list[TreeNode] = []
        for node in queue:
            if node.left is not None:
                next_level.append(node.left)
            if node.right is not None:
                next_level.append(node.right)
        queue = next_level
        left_to_right = not left_to_right
    return out


def solve_kth_smallest(root: TreeNode | None, k: int) -> int:
    stack: list[TreeNode] = []
    current = root
    while current is not None or stack:
        while current is not None:
            stack.append(current)
            current = current.left
        current = stack.pop()
        k -= 1
        if k == 0:
            return current.val
        current = current.right
    return -1


def solve_build_tree(preorder: list[int], inorder: list[int]) -> TreeNode | None:
    index_by_value = {value: idx for idx, value in enumerate(inorder)}
    pre_idx = 0

    def build(left: int, right: int) -> TreeNode | None:
        nonlocal pre_idx
        if left > right:
            return None
        root_val = preorder[pre_idx]
        pre_idx += 1
        mid = index_by_value[root_val]
        root = TreeNode(root_val)
        root.left = build(left, mid - 1)
        root.right = build(mid + 1, right)
        return root

    return build(0, len(inorder) - 1)


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


def solve_transform_sum_tree(root: TreeNode | None) -> TreeNode | None:
    working = clone_tree(root)

    def dfs(node: TreeNode | None) -> int:
        if node is None:
            return 0
        original = node.val
        left_sum = dfs(node.left)
        right_sum = dfs(node.right)
        node.val = left_sum + right_sum
        return node.val + original

    dfs(working)
    return working


def build_balanced_cases() -> list[dict]:
    cases: list[dict] = []
    idx = 0
    samples = [
        ([3, 9, 20, None, None, 15, 7], True),
        ([1, 2, 2, 3, 3, None, None, 4, 4], False),
    ]
    for values, expected in samples:
        cases.append(make_case(values, expected_output=expected, idx=idx, is_sample=True))
        idx += 1

    fixed_values = [
        [],
        [1],
        [1, 2, 2, 3, 3, 3, 3],
        make_skewed([1, 2, 3, 4], left=True),
        make_skewed([1, 2, 3, 4], left=False),
        [1, 2, None, 3, None, 4, None],
        [1, 2, 2, 3, None, None, 3, 4, None, None, 4],
        [10, 5, 15, 2, 7, 12, 20],
    ]
    for values in fixed_values:
        cases.append(make_case(values, expected_output=solve_is_balanced(build_tree(values)), idx=idx))
        idx += 1

    rng = random.Random(2026040411)
    while len(cases) < TARGET_CASES:
        values = random_tree_array(rng, max_nodes=rng.randint(0, 200), allow_empty=True, value_low=-500, value_high=500)
        cases.append(make_case(values, expected_output=solve_is_balanced(build_tree(values)), idx=idx))
        idx += 1
    return cases


def build_diameter_cases() -> list[dict]:
    cases: list[dict] = []
    idx = 0
    samples = [
        ([1, 2, 3, 4, 5], 3),
        ([1, 2], 1),
    ]
    for values, expected in samples:
        cases.append(make_case(values, expected_output=expected, idx=idx, is_sample=True))
        idx += 1

    fixed_values = [
        [],
        [1],
        [1, 2, 3],
        make_skewed([1, 2, 3, 4, 5, 6], left=True),
        make_skewed([1, 2, 3, 4, 5, 6], left=False),
        [1, 2, 3, 4, None, None, 5],
        [4, 2, 7, 1, 3, 6, 9],
    ]
    for values in fixed_values:
        cases.append(make_case(values, expected_output=solve_diameter(build_tree(values)), idx=idx))
        idx += 1

    rng = random.Random(2026040412)
    while len(cases) < TARGET_CASES:
        values = random_tree_array(rng, max_nodes=rng.randint(0, 220), allow_empty=True, value_low=-500, value_high=500)
        cases.append(make_case(values, expected_output=solve_diameter(build_tree(values)), idx=idx))
        idx += 1
    return cases


def build_path_sum_cases() -> list[dict]:
    cases: list[dict] = []
    idx = 0
    samples = [
        ([5, 4, 8, 11, None, 13, 4, 7, 2, None, None, None, 1], 22, True),
        ([1, 2, 3], 5, False),
    ]
    for values, target, expected in samples:
        cases.append(make_case(values, target, expected_output=expected, idx=idx, is_sample=True))
        idx += 1

    fixed = [
        ([], 0, False),
        ([1], 1, True),
        ([1], 2, False),
        ([1, 2], 3, True),
        ([1, 2, 3], 4, True),
        ([1, 2, 3], 5, False),
        ([-2, None, -3], -5, True),
        ([1, -2, -3, 1, 3, -2, None, -1], -1, True),
    ]
    for values, target, expected in fixed:
        cases.append(make_case(values, target, expected_output=expected, idx=idx))
        idx += 1

    rng = random.Random(2026040413)
    while len(cases) < TARGET_CASES:
        values = random_tree_array(rng, max_nodes=rng.randint(1, 180), allow_empty=False, value_low=-100, value_high=100)
        root = build_tree(values)
        if rng.random() < 0.6:
            node = root
            target = 0
            while node is not None:
                target += node.val
                if node.left is None and node.right is None:
                    break
                if node.left is not None and node.right is not None:
                    node = node.left if rng.random() < 0.5 else node.right
                else:
                    node = node.left if node.left is not None else node.right
        else:
            target = rng.randint(-500, 500)
        cases.append(make_case(values, target, expected_output=solve_has_path_sum(root, target), idx=idx))
        idx += 1
    return cases


def build_symmetric_cases() -> list[dict]:
    cases: list[dict] = []
    idx = 0
    samples = [
        ([1, 2, 2, 3, 4, 4, 3], True),
        ([1, 2, 2, None, 3, None, 3], False),
    ]
    for values, expected in samples:
        cases.append(make_case(values, expected_output=expected, idx=idx, is_sample=True))
        idx += 1

    fixed_values = [
        [],
        [1],
        [1, 2, 2],
        [1, 2, 2, 3, 4, 4, 3],
        [1, 2, 2, None, 3, 3, None],
        [1, 2, 2, 3, None, None, 3],
        [1, 2, 2, 3, 4, 4, 5],
        [1, 2, 2, None, 3, None, 4],
    ]
    for values in fixed_values:
        cases.append(make_case(values, expected_output=solve_symmetric(build_tree(values)), idx=idx))
        idx += 1

    rng = random.Random(2026040414)
    while len(cases) < TARGET_CASES:
        if rng.random() < 0.45:
            half = random_tree_array(rng, max_nodes=rng.randint(0, 70), allow_empty=True, value_low=-50, value_high=50)
            left = build_tree(half)

            def mirror(node: TreeNode | None) -> TreeNode | None:
                if node is None:
                    return None
                return TreeNode(node.val, mirror(node.right), mirror(node.left))

            root = TreeNode(rng.randint(-20, 20), clone_tree(left), mirror(left))
            values = tree_to_array(root)
        else:
            values = random_tree_array(rng, max_nodes=rng.randint(0, 140), allow_empty=True, value_low=-50, value_high=50)
        cases.append(make_case(values, expected_output=solve_symmetric(build_tree(values)), idx=idx))
        idx += 1
    return cases


def build_min_depth_cases() -> list[dict]:
    cases: list[dict] = []
    idx = 0
    samples = [
        ([3, 9, 20, None, None, 15, 7], 2),
        ([2, None, 3, None, 4, None, 5, None, 6], 5),
    ]
    for values, expected in samples:
        cases.append(make_case(values, expected_output=expected, idx=idx, is_sample=True))
        idx += 1

    fixed_values = [
        [],
        [1],
        [1, 2, 3],
        [1, 2, None, 3, None, 4],
        [1, None, 2, None, 3, None, 4],
        [10, 5, 15, 2, 7, 12, 20],
    ]
    for values in fixed_values:
        cases.append(make_case(values, expected_output=solve_min_depth(build_tree(values)), idx=idx))
        idx += 1

    rng = random.Random(2026040415)
    while len(cases) < TARGET_CASES:
        values = random_tree_array(rng, max_nodes=rng.randint(0, 180), allow_empty=True, value_low=-100, value_high=100)
        cases.append(make_case(values, expected_output=solve_min_depth(build_tree(values)), idx=idx))
        idx += 1
    return cases


def build_right_side_cases() -> list[dict]:
    cases: list[dict] = []
    idx = 0
    samples = [
        ([1, 2, 3, None, 5, None, 4], [1, 3, 4]),
        ([1, None, 3], [1, 3]),
    ]
    for values, expected in samples:
        cases.append(make_case(values, expected_output=expected, idx=idx, is_sample=True))
        idx += 1

    fixed_values = [
        [],
        [1],
        [1, 2, 3],
        make_skewed([1, 2, 3, 4], left=True),
        make_skewed([1, 2, 3, 4], left=False),
        [1, 2, 3, 4, None, None, 5],
    ]
    for values in fixed_values:
        cases.append(make_case(values, expected_output=solve_right_side_view(build_tree(values)), idx=idx))
        idx += 1

    rng = random.Random(2026040416)
    while len(cases) < TARGET_CASES:
        values = random_tree_array(rng, max_nodes=rng.randint(0, 200), allow_empty=True, value_low=-200, value_high=200)
        cases.append(make_case(values, expected_output=solve_right_side_view(build_tree(values)), idx=idx))
        idx += 1
    return cases


def build_zigzag_cases() -> list[dict]:
    cases: list[dict] = []
    idx = 0
    samples = [
        ([3, 9, 20, None, None, 15, 7], [[3], [20, 9], [15, 7]]),
        ([1], [[1]]),
    ]
    for values, expected in samples:
        cases.append(make_case(values, expected_output=expected, idx=idx, is_sample=True))
        idx += 1

    fixed_values = [
        [],
        [1, 2, 3, 4, 5, 6, 7],
        make_skewed([1, 2, 3, 4], left=True),
        make_skewed([1, 2, 3, 4], left=False),
        [1, 2, 3, None, 4, 5, None],
    ]
    for values in fixed_values:
        cases.append(make_case(values, expected_output=solve_zigzag(build_tree(values)), idx=idx))
        idx += 1

    rng = random.Random(2026040417)
    while len(cases) < TARGET_CASES:
        values = random_tree_array(rng, max_nodes=rng.randint(0, 180), allow_empty=True, value_low=-200, value_high=200)
        cases.append(make_case(values, expected_output=solve_zigzag(build_tree(values)), idx=idx))
        idx += 1
    return cases


def build_kth_smallest_cases() -> list[dict]:
    cases: list[dict] = []
    idx = 0
    samples = [
        ([3, 1, 4, None, 2], 1, 1),
        ([5, 3, 6, 2, 4, None, None, 1], 3, 3),
    ]
    for values, k, expected in samples:
        cases.append(make_case(values, k, expected_output=expected, idx=idx, is_sample=True))
        idx += 1

    fixed = [
        ([2, 1, 3], 1, 1),
        ([2, 1, 3], 2, 2),
        ([2, 1, 3], 3, 3),
        ([20, 8, 22, 4, 12, None, None, None, None, 10, 14], 3, 10),
    ]
    for values, k, expected in fixed:
        cases.append(make_case(values, k, expected_output=expected, idx=idx))
        idx += 1

    rng = random.Random(2026040418)
    while len(cases) < TARGET_CASES:
        values = random_bst_array(rng, size=rng.randint(1, 140), low=-3000, high=3000)
        root = build_tree(values)
        total = len(inorder_values(root))
        k = rng.randint(1, total)
        cases.append(make_case(values, k, expected_output=solve_kth_smallest(root, k), idx=idx))
        idx += 1
    return cases


def build_construct_cases() -> list[dict]:
    cases: list[dict] = []
    idx = 0
    samples = [
        ([3, 9, 20, 15, 7], [9, 3, 15, 20, 7], [3, 9, 20, None, None, 15, 7]),
        ([-1], [-1], [-1]),
    ]
    for preorder, inorder, expected in samples:
        cases.append(make_case(preorder, inorder, expected_output=expected, idx=idx, is_sample=True))
        idx += 1

    fixed_trees = [
        [1],
        [1, 2, 3],
        make_skewed([1, 2, 3, 4], left=True),
        make_skewed([1, 2, 3, 4], left=False),
        [4, 2, 7, 1, 3, 6, 9],
    ]
    for values in fixed_trees:
        root = build_tree(values)
        cases.append(
            make_case(
                preorder_values(root),
                inorder_values(root),
                expected_output=tree_to_array(solve_build_tree(preorder_values(root), inorder_values(root))),
                idx=idx,
            )
        )
        idx += 1

    rng = random.Random(2026040419)
    while len(cases) < TARGET_CASES:
        values = random_unique_tree_array(rng, max_nodes=rng.randint(1, 120), allow_empty=False, value_low=-5000, value_high=5000)
        root = build_tree(values)
        preorder = preorder_values(root)
        inorder = inorder_values(root)
        cases.append(
            make_case(
                preorder,
                inorder,
                expected_output=tree_to_array(solve_build_tree(preorder, inorder)),
                idx=idx,
            )
        )
        idx += 1
    return cases


def build_transform_sum_tree_cases() -> list[dict]:
    cases: list[dict] = []
    idx = 0
    samples = [
        ([10, -2, 6, 8, -4, 7, 5], [20, 4, 12, 0, 0, 0, 0]),
        ([1], [0]),
    ]
    for values, expected in samples:
        cases.append(make_case(values, expected_output=expected, idx=idx, is_sample=True))
        idx += 1

    fixed_values = [
        [],
        [1, 2, 3],
        [5, 2, -3],
        [4, 1, 6, 0, 2, 5, 7],
        [10, -2, 6, 8, -4, 7, 5, 2, -2, 3, -5, 9, -8, 2, 8],
    ]
    for values in fixed_values:
        cases.append(make_case(values, expected_output=tree_to_array(solve_transform_sum_tree(build_tree(values))), idx=idx))
        idx += 1

    rng = random.Random(2026040420)
    while len(cases) < TARGET_CASES:
        values = random_tree_array(rng, max_nodes=rng.randint(0, 160), allow_empty=True, value_low=-200, value_high=200)
        cases.append(make_case(values, expected_output=tree_to_array(solve_transform_sum_tree(build_tree(values))), idx=idx))
        idx += 1
    return cases


PROBLEMS = [
    (
        "Balanced Binary Tree",
        build_balanced_cases,
        dict(
            description="Given the root of a binary tree, determine if the height difference between the left and right subtree of every node is at most one.",
            difficulty=Difficulty.EASY,
            input_format="Line 1: JSON array root in level-order form using null for missing children",
            output_format="Boolean true/false",
            constraints="0 <= number of nodes <= 5000\n-10^4 <= Node.val <= 10^4",
            method_name="isBalanced",
            parameters=[{"name": "root", "type": "TreeNode"}],
            return_type="bool",
            time_limit_ms=1500,
            memory_limit_mb=256,
            rating=950,
            is_active=True,
        ),
    ),
    (
        "Diameter of Binary Tree",
        build_diameter_cases,
        dict(
            description="The diameter of a binary tree is the length of the longest path between any two nodes. Return the diameter of the tree.",
            difficulty=Difficulty.EASY,
            input_format="Line 1: JSON array root in level-order form using null for missing children",
            output_format="Single integer: the diameter of the binary tree",
            constraints="1 <= number of nodes <= 10^4\n-10^5 <= Node.val <= 10^5",
            method_name="diameterOfBinaryTree",
            parameters=[{"name": "root", "type": "TreeNode"}],
            return_type="int",
            time_limit_ms=1500,
            memory_limit_mb=256,
            rating=1000,
            is_active=True,
        ),
    ),
    (
        "Path Sum",
        build_path_sum_cases,
        dict(
            description="Given the root of a binary tree and an integer targetSum, return true if the tree has a root-to-leaf path such that adding up all the values along the path equals targetSum.",
            difficulty=Difficulty.EASY,
            input_format="Line 1: JSON array root in level-order form using null for missing children\nLine 2: integer targetSum",
            output_format="Boolean true/false",
            constraints="0 <= number of nodes <= 5000\n-1000 <= Node.val <= 1000\n-10^5 <= targetSum <= 10^5",
            method_name="hasPathSum",
            parameters=[{"name": "root", "type": "TreeNode"}, {"name": "targetSum", "type": "int"}],
            return_type="bool",
            time_limit_ms=1500,
            memory_limit_mb=256,
            rating=950,
            is_active=True,
        ),
    ),
    (
        "Symmetric Tree",
        build_symmetric_cases,
        dict(
            description="Given the root of a binary tree, check whether it is a mirror of itself around its center.",
            difficulty=Difficulty.EASY,
            input_format="Line 1: JSON array root in level-order form using null for missing children",
            output_format="Boolean true/false",
            constraints="0 <= number of nodes <= 2000\n-100 <= Node.val <= 100",
            method_name="isSymmetric",
            parameters=[{"name": "root", "type": "TreeNode"}],
            return_type="bool",
            time_limit_ms=1500,
            memory_limit_mb=256,
            rating=1000,
            is_active=True,
        ),
    ),
    (
        "Minimum Depth of Binary Tree",
        build_min_depth_cases,
        dict(
            description="Given the root of a binary tree, return its minimum depth. The minimum depth is the number of nodes along the shortest path from the root down to the nearest leaf node.",
            difficulty=Difficulty.EASY,
            input_format="Line 1: JSON array root in level-order form using null for missing children",
            output_format="Single integer: the minimum depth of the binary tree",
            constraints="0 <= number of nodes <= 10^5\n-1000 <= Node.val <= 1000",
            method_name="minDepth",
            parameters=[{"name": "root", "type": "TreeNode"}],
            return_type="int",
            time_limit_ms=1500,
            memory_limit_mb=256,
            rating=950,
            is_active=True,
        ),
    ),
    (
        "Binary Tree Right Side View",
        build_right_side_cases,
        dict(
            description="Given the root of a binary tree, imagine yourself standing on the right side of it. Return the values of the nodes you can see ordered from top to bottom.",
            difficulty=Difficulty.MEDIUM,
            input_format="Line 1: JSON array root in level-order form using null for missing children",
            output_format="JSON array containing the visible right-side values",
            constraints="0 <= number of nodes <= 100\n-100 <= Node.val <= 100",
            method_name="rightSideView",
            parameters=[{"name": "root", "type": "TreeNode"}],
            return_type="int[]",
            time_limit_ms=1500,
            memory_limit_mb=256,
            rating=1150,
            is_active=True,
        ),
    ),
    (
        "Binary Tree Zigzag Level Order Traversal",
        build_zigzag_cases,
        dict(
            description="Given the root of a binary tree, return the zigzag level order traversal of its nodes' values from left to right, then right to left for the next level, and so on.",
            difficulty=Difficulty.MEDIUM,
            input_format="Line 1: JSON array root in level-order form using null for missing children",
            output_format="JSON matrix containing the zigzag level-order traversal",
            constraints="0 <= number of nodes <= 2000\n-100 <= Node.val <= 100",
            method_name="zigzagLevelOrder",
            parameters=[{"name": "root", "type": "TreeNode"}],
            return_type="int[][]",
            time_limit_ms=1500,
            memory_limit_mb=256,
            rating=1200,
            is_active=True,
        ),
    ),
    (
        "Kth Smallest Element in a BST",
        build_kth_smallest_cases,
        dict(
            description="Given the root of a binary search tree and an integer k, return the kth smallest value in the tree.",
            difficulty=Difficulty.MEDIUM,
            input_format="Line 1: JSON array root in level-order form using null for missing children\nLine 2: integer k",
            output_format="Single integer: the kth smallest value",
            constraints="1 <= number of nodes <= 10^4\n1 <= k <= n\n-10^4 <= Node.val <= 10^4",
            method_name="kthSmallest",
            parameters=[{"name": "root", "type": "TreeNode"}, {"name": "k", "type": "int"}],
            return_type="int",
            time_limit_ms=1500,
            memory_limit_mb=256,
            rating=1200,
            is_active=True,
        ),
    ),
    (
        "Construct Binary Tree from Preorder and Inorder Traversal",
        build_construct_cases,
        dict(
            description="Given two integer arrays preorder and inorder where preorder is the preorder traversal of a binary tree and inorder is the inorder traversal of the same tree, construct and return the binary tree.",
            difficulty=Difficulty.MEDIUM,
            input_format="Line 1: JSON array preorder\nLine 2: JSON array inorder",
            output_format="JSON array of the constructed tree in level-order form using null for missing children",
            constraints="1 <= preorder.length <= 300\ninorder.length == preorder.length\n-3000 <= preorder[i], inorder[i] <= 3000\npreorder and inorder consist of unique values",
            method_name="buildTree",
            parameters=[{"name": "preorder", "type": "int[]"}, {"name": "inorder", "type": "int[]"}],
            return_type="TreeNode",
            time_limit_ms=1800,
            memory_limit_mb=256,
            rating=1300,
            is_active=True,
        ),
    ),
    (
        "Transform to Sum Tree",
        build_transform_sum_tree_cases,
        dict(
            description="Given the root of a binary tree, convert it into a sum tree where each node stores the sum of the values present in its left and right subtrees in the original tree. Leaf nodes become 0.",
            difficulty=Difficulty.MEDIUM,
            input_format="Line 1: JSON array root in level-order form using null for missing children",
            output_format="JSON array of the transformed sum tree in level-order form using null for missing children",
            constraints="0 <= number of nodes <= 10^4\n-10^4 <= Node.val <= 10^4",
            method_name="toSumTree",
            parameters=[{"name": "root", "type": "TreeNode"}],
            return_type="TreeNode",
            time_limit_ms=1800,
            memory_limit_mb=256,
            rating=1300,
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
