from __future__ import annotations

import asyncio
import random
from collections import defaultdict, deque

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.config import settings
from backend.core.constants import Difficulty
from backend.scripts.array_seed_utils import make_case, upsert_problem
from backend.scripts.seed_even_more_binary_tree_problems import random_unique_tree_array
from backend.scripts.seed_more_binary_tree_problems import (
    TARGET_CASES,
    TreeNode,
    build_tree,
    clone_tree,
    random_bst_array,
    random_tree_array,
    tree_to_array,
)

MOD = 1_000_000_007


def inorder_values(root: TreeNode | None) -> list[int]:
    if root is None:
        return []
    return inorder_values(root.left) + [root.val] + inorder_values(root.right)


def preorder_nodes(root: TreeNode | None) -> list[TreeNode]:
    if root is None:
        return []
    return [root] + preorder_nodes(root.left) + preorder_nodes(root.right)


def solve_recover_bst(root: TreeNode | None) -> TreeNode | None:
    working = clone_tree(root)
    first = None
    second = None
    prev = None

    def dfs(node: TreeNode | None) -> None:
        nonlocal first, second, prev
        if node is None:
            return
        dfs(node.left)
        if prev is not None and prev.val > node.val:
            if first is None:
                first = prev
            second = node
        prev = node
        dfs(node.right)

    dfs(working)
    if first is not None and second is not None:
        first.val, second.val = second.val, first.val
    return working


def solve_min_camera_cover(root: TreeNode | None) -> int:
    cameras = 0

    def dfs(node: TreeNode | None) -> int:
        nonlocal cameras
        if node is None:
            return 0
        left = dfs(node.left)
        right = dfs(node.right)
        if left == -1 or right == -1:
            cameras += 1
            return 1
        if left == 1 or right == 1:
            return 0
        return -1

    if dfs(root) == -1:
        cameras += 1
    return cameras


def solve_house_robber_iii(root: TreeNode | None) -> int:
    def dfs(node: TreeNode | None) -> tuple[int, int]:
        if node is None:
            return 0, 0
        left_take, left_skip = dfs(node.left)
        right_take, right_skip = dfs(node.right)
        take = node.val + left_skip + right_skip
        skip = max(left_take, left_skip) + max(right_take, right_skip)
        return take, skip

    take, skip = dfs(root)
    return max(take, skip)


def solve_distance_k(root: TreeNode | None, target: int, k: int) -> list[int]:
    if root is None:
        return []
    graph: dict[int, list[int]] = defaultdict(list)

    def build(node: TreeNode | None) -> None:
        if node is None:
            return
        if node.left is not None:
            graph[node.val].append(node.left.val)
            graph[node.left.val].append(node.val)
            build(node.left)
        if node.right is not None:
            graph[node.val].append(node.right.val)
            graph[node.right.val].append(node.val)
            build(node.right)

    build(root)
    queue = deque([(target, 0)])
    seen = {target}
    out: list[int] = []
    while queue:
        node, dist = queue.popleft()
        if dist == k:
            out.append(node)
            continue
        for nxt in graph[node]:
            if nxt not in seen:
                seen.add(nxt)
                queue.append((nxt, dist + 1))
    return sorted(out)


def solve_max_sum_bst(root: TreeNode | None) -> int:
    best = 0

    def dfs(node: TreeNode | None) -> tuple[bool, int, int, int]:
        nonlocal best
        if node is None:
            return True, 10**18, -10**18, 0
        left_ok, left_min, left_max, left_sum = dfs(node.left)
        right_ok, right_min, right_max, right_sum = dfs(node.right)
        if left_ok and right_ok and left_max < node.val < right_min:
            total = left_sum + right_sum + node.val
            best = max(best, total)
            return True, min(left_min, node.val), max(right_max, node.val), total
        return False, -10**18, 10**18, 0

    dfs(root)
    return best


def solve_distribute_coins(root: TreeNode | None) -> int:
    moves = 0

    def dfs(node: TreeNode | None) -> int:
        nonlocal moves
        if node is None:
            return 0
        left = dfs(node.left)
        right = dfs(node.right)
        moves += abs(left) + abs(right)
        return node.val + left + right - 1

    dfs(root)
    return moves


def solve_max_product(root: TreeNode | None) -> int:
    totals: list[int] = []

    def sums(node: TreeNode | None) -> int:
        if node is None:
            return 0
        total = node.val + sums(node.left) + sums(node.right)
        totals.append(total)
        return total

    total = sums(root)
    best = 0
    for part in totals:
        best = max(best, part * (total - part))
    return best % MOD


def solve_smallest_from_leaf(root: TreeNode | None) -> str:
    best = None

    def dfs(node: TreeNode | None, suffix: str) -> None:
        nonlocal best
        if node is None:
            return
        current = chr(ord("a") + node.val) + suffix
        if node.left is None and node.right is None:
            if best is None or current < best:
                best = current
            return
        dfs(node.left, current)
        dfs(node.right, current)

    dfs(root, "")
    return best or ""


def solve_vertical_traversal(root: TreeNode | None) -> list[list[int]]:
    if root is None:
        return []
    cols: dict[int, list[tuple[int, int]]] = defaultdict(list)
    queue = deque([(root, 0, 0)])
    while queue:
        node, row, col = queue.popleft()
        cols[col].append((row, node.val))
        if node.left is not None:
            queue.append((node.left, row + 1, col - 1))
        if node.right is not None:
            queue.append((node.right, row + 1, col + 1))
    out = []
    for col in sorted(cols):
        out.append([val for _, val in sorted(cols[col])])
    return out


def solve_boundary(root: TreeNode | None) -> list[int]:
    if root is None:
        return []
    if root.left is None and root.right is None:
        return [root.val]

    out = [root.val]

    def add_left(node: TreeNode | None) -> None:
        cur = node
        while cur is not None:
            if cur.left is not None or cur.right is not None:
                out.append(cur.val)
            cur = cur.left if cur.left is not None else cur.right

    def add_leaves(node: TreeNode | None) -> None:
        if node is None:
            return
        if node.left is None and node.right is None:
            out.append(node.val)
            return
        add_leaves(node.left)
        add_leaves(node.right)

    def right_values(node: TreeNode | None) -> list[int]:
        vals: list[int] = []
        cur = node
        while cur is not None:
            if cur.left is not None or cur.right is not None:
                vals.append(cur.val)
            cur = cur.right if cur.right is not None else cur.left
        vals.reverse()
        return vals

    add_left(root.left)
    add_leaves(root.left)
    add_leaves(root.right)
    out.extend(right_values(root.right))
    return out


def choose_target_value(root: TreeNode | None, rng: random.Random) -> int:
    vals = inorder_values(root)
    return rng.choice(vals)


def swap_two_nodes_in_bst(values: list[int | None], rng: random.Random) -> list[int | None]:
    root = build_tree(values)
    nodes = preorder_nodes(root)
    if len(nodes) < 2:
        return values
    a, b = rng.sample(nodes, 2)
    a.val, b.val = b.val, a.val
    return tree_to_array(root)


def random_coin_tree_array(rng: random.Random, max_nodes: int) -> list[int | None]:
    template = random_tree_array(rng, max_nodes=max_nodes, allow_empty=False, value_low=0, value_high=0, null_bias=0.28)
    count = sum(v is not None for v in template)
    if count == 0:
        return [1]
    coins = [0] * count
    remaining = count
    for idx in range(count):
        if idx == count - 1:
            coins[idx] += remaining
        else:
            give = rng.randint(0, remaining)
            coins[idx] += give
            remaining -= give
    rng.shuffle(coins)
    it = iter(coins)
    out = [next(it) if v is not None else None for v in template]
    while out and out[-1] is None:
        out.pop()
    return out


def build_recover_bst_cases() -> list[dict]:
    cases = []
    idx = 0
    samples = [
        ([1, 3, None, None, 2], [3, 1, None, None, 2]),
        ([3, 1, 4, None, None, 2], [2, 1, 4, None, None, 3]),
    ]
    for values, expected in samples:
        cases.append(make_case(values, expected_output=expected, idx=idx, is_sample=True))
        idx += 1

    rng = random.Random(2026040440)
    while len(cases) < TARGET_CASES:
        bst_values = random_bst_array(rng, size=rng.randint(2, 140), low=-4000, high=4000)
        broken = swap_two_nodes_in_bst(bst_values, rng)
        cases.append(make_case(broken, expected_output=tree_to_array(solve_recover_bst(build_tree(broken))), idx=idx))
        idx += 1
    return cases


def build_camera_cases() -> list[dict]:
    cases = []
    idx = 0
    samples = [
        ([0, 0, None, 0, 0], 1),
        ([0, 0, None, 0, None, 0, None, None, 0], 2),
    ]
    for values, expected in samples:
        cases.append(make_case(values, expected_output=expected, idx=idx, is_sample=True))
        idx += 1

    rng = random.Random(2026040441)
    fixed = [[], [0], [0, 0], [0, 0, 0], [0, None, 0, None, 0], [0, 0, None, 0, 0]]
    for values in fixed:
        cases.append(make_case(values, expected_output=solve_min_camera_cover(build_tree(values)), idx=idx))
        idx += 1

    while len(cases) < TARGET_CASES:
        values = random_tree_array(rng, max_nodes=rng.randint(0, 180), allow_empty=True, value_low=0, value_high=0, null_bias=0.32)
        cases.append(make_case(values, expected_output=solve_min_camera_cover(build_tree(values)), idx=idx))
        idx += 1
    return cases


def build_house_robber_cases() -> list[dict]:
    cases = []
    idx = 0
    samples = [
        ([3, 2, 3, None, 3, None, 1], 7),
        ([3, 4, 5, 1, 3, None, 1], 9),
    ]
    for values, expected in samples:
        cases.append(make_case(values, expected_output=expected, idx=idx, is_sample=True))
        idx += 1

    rng = random.Random(2026040442)
    while len(cases) < TARGET_CASES:
        values = random_tree_array(rng, max_nodes=rng.randint(0, 180), allow_empty=True, value_low=0, value_high=1000, null_bias=0.3)
        cases.append(make_case(values, expected_output=solve_house_robber_iii(build_tree(values)), idx=idx))
        idx += 1
    return cases


def build_distance_k_cases() -> list[dict]:
    cases = []
    idx = 0
    samples = [
        ([3, 5, 1, 6, 2, 0, 8, None, None, 7, 4], 5, 2, [1, 4, 7]),
        ([1], 1, 3, []),
    ]
    for values, target, k, expected in samples:
        cases.append(make_case(values, target, k, expected_output=expected, idx=idx, is_sample=True))
        idx += 1

    rng = random.Random(2026040443)
    while len(cases) < TARGET_CASES:
        values = random_unique_tree_array(rng, max_nodes=rng.randint(1, 180), allow_empty=False, value_low=1, value_high=5000)
        root = build_tree(values)
        target = choose_target_value(root, rng)
        k = rng.randint(0, min(25, max(1, len(inorder_values(root)))))
        cases.append(make_case(values, target, k, expected_output=solve_distance_k(root, target, k), idx=idx))
        idx += 1
    return cases


def build_max_sum_bst_cases() -> list[dict]:
    cases = []
    idx = 0
    samples = [
        ([1, 4, 3, 2, 4, 2, 5, None, None, None, None, None, None, 4, 6], 20),
        ([4, 3, None, 1, 2], 2),
    ]
    for values, expected in samples:
        cases.append(make_case(values, expected_output=expected, idx=idx, is_sample=True))
        idx += 1

    rng = random.Random(2026040444)
    while len(cases) < TARGET_CASES:
        values = random_tree_array(rng, max_nodes=rng.randint(0, 180), allow_empty=True, value_low=-1000, value_high=1000)
        cases.append(make_case(values, expected_output=solve_max_sum_bst(build_tree(values)), idx=idx))
        idx += 1
    return cases


def build_distribute_coins_cases() -> list[dict]:
    cases = []
    idx = 0
    samples = [
        ([3, 0, 0], 2),
        ([0, 3, 0], 3),
    ]
    for values, expected in samples:
        cases.append(make_case(values, expected_output=expected, idx=idx, is_sample=True))
        idx += 1

    rng = random.Random(2026040445)
    while len(cases) < TARGET_CASES:
        values = random_coin_tree_array(rng, rng.randint(1, 140))
        cases.append(make_case(values, expected_output=solve_distribute_coins(build_tree(values)), idx=idx))
        idx += 1
    return cases


def build_max_product_cases() -> list[dict]:
    cases = []
    idx = 0
    samples = [
        ([1, 2, 3, 4, 5, 6], 110),
        ([1, None, 2, 3, 4, None, None, 5, 6], 90),
    ]
    for values, expected in samples:
        cases.append(make_case(values, expected_output=expected, idx=idx, is_sample=True))
        idx += 1

    rng = random.Random(2026040446)
    while len(cases) < TARGET_CASES:
        values = random_tree_array(rng, max_nodes=rng.randint(1, 180), allow_empty=False, value_low=1, value_high=1000)
        cases.append(make_case(values, expected_output=solve_max_product(build_tree(values)), idx=idx))
        idx += 1
    return cases


def build_smallest_leaf_string_cases() -> list[dict]:
    cases = []
    idx = 0
    samples = [
        ([0, 1, 2, 3, 4, 3, 4], "dba"),
        ([25, 1, 3, 1, 3, 0, 2], "adz"),
    ]
    for values, expected in samples:
        cases.append(make_case(values, expected_output=expected, idx=idx, is_sample=True))
        idx += 1

    rng = random.Random(2026040447)
    while len(cases) < TARGET_CASES:
        values = random_tree_array(rng, max_nodes=rng.randint(1, 160), allow_empty=False, value_low=0, value_high=25)
        cases.append(make_case(values, expected_output=solve_smallest_from_leaf(build_tree(values)), idx=idx))
        idx += 1
    return cases


def build_vertical_cases() -> list[dict]:
    cases = []
    idx = 0
    samples = [
        ([3, 9, 20, None, None, 15, 7], [[9], [3, 15], [20], [7]]),
        ([1, 2, 3, 4, 5, 6, 7], [[4], [2], [1, 5, 6], [3], [7]]),
    ]
    for values, expected in samples:
        cases.append(make_case(values, expected_output=expected, idx=idx, is_sample=True))
        idx += 1

    rng = random.Random(2026040448)
    while len(cases) < TARGET_CASES:
        values = random_tree_array(rng, max_nodes=rng.randint(0, 170), allow_empty=True, value_low=-1000, value_high=1000)
        cases.append(make_case(values, expected_output=solve_vertical_traversal(build_tree(values)), idx=idx))
        idx += 1
    return cases


def build_boundary_cases() -> list[dict]:
    cases = []
    idx = 0
    samples = [
        ([1, None, 2, 3, 4], [1, 3, 4, 2]),
        ([1, 2, 3, 4, 5, 6, 7], [1, 2, 4, 5, 6, 7, 3]),
    ]
    for values, expected in samples:
        cases.append(make_case(values, expected_output=expected, idx=idx, is_sample=True))
        idx += 1

    rng = random.Random(2026040449)
    fixed = [[], [1], [1, 2], [1, None, 2], [1, 2, 3], [1, 2, None, 3, 4]]
    for values in fixed:
        cases.append(make_case(values, expected_output=solve_boundary(build_tree(values)), idx=idx))
        idx += 1

    while len(cases) < TARGET_CASES:
        values = random_tree_array(rng, max_nodes=rng.randint(0, 180), allow_empty=True, value_low=-500, value_high=500)
        cases.append(make_case(values, expected_output=solve_boundary(build_tree(values)), idx=idx))
        idx += 1
    return cases


PROBLEMS = [
    (
        "Recover Binary Search Tree",
        build_recover_bst_cases,
        dict(
            description="Two nodes of a binary search tree have been swapped by mistake. Recover the tree without changing its structure and return the corrected root.",
            difficulty=Difficulty.HARD,
            input_format="Line 1: JSON array root in level-order form using null for missing children",
            output_format="JSON array of the recovered BST in level-order form using null for missing children",
            constraints="2 <= number of nodes <= 10^4\n-10^5 <= Node.val <= 10^5",
            method_name="recoverTreeFixed",
            parameters=[{"name": "root", "type": "TreeNode"}],
            return_type="TreeNode",
            time_limit_ms=2000,
            memory_limit_mb=256,
            rating=1550,
            is_active=True,
        ),
    ),
    (
        "Binary Tree Cameras",
        build_camera_cases,
        dict(
            description="Install cameras on tree nodes so that every node is monitored by a camera on itself, its parent, or one of its children. Return the minimum number of cameras needed.",
            difficulty=Difficulty.HARD,
            input_format="Line 1: JSON array root in level-order form using null for missing children",
            output_format="Single integer: the minimum number of cameras",
            constraints="1 <= number of nodes <= 1000\nNode.val is always 0 in generated tests",
            method_name="minCameraCover",
            parameters=[{"name": "root", "type": "TreeNode"}],
            return_type="int",
            time_limit_ms=2000,
            memory_limit_mb=256,
            rating=1600,
            is_active=True,
        ),
    ),
    (
        "House Robber III",
        build_house_robber_cases,
        dict(
            description="A thief cannot rob two directly-linked houses in a binary tree neighborhood. Return the maximum amount of money that can be robbed without alerting the police.",
            difficulty=Difficulty.HARD,
            input_format="Line 1: JSON array root in level-order form using null for missing children",
            output_format="Single integer: the maximum loot",
            constraints="0 <= number of nodes <= 10^4\n0 <= Node.val <= 10^4",
            method_name="rob",
            parameters=[{"name": "root", "type": "TreeNode"}],
            return_type="int",
            time_limit_ms=2000,
            memory_limit_mb=256,
            rating=1550,
            is_active=True,
        ),
    ),
    (
        "All Nodes Distance K in Binary Tree",
        build_distance_k_cases,
        dict(
            description="Given the root of a binary tree, a target node value, and an integer k, return all node values at distance k from the target. Return the answer sorted in ascending order.",
            difficulty=Difficulty.HARD,
            input_format="Line 1: JSON array root in level-order form using null for missing children\nLine 2: integer target\nLine 3: integer k",
            output_format="JSON array of node values sorted in ascending order",
            constraints="1 <= number of nodes <= 5 * 10^4\nAll Node.val values are unique\n0 <= k <= 5 * 10^4",
            method_name="distanceKValues",
            parameters=[{"name": "root", "type": "TreeNode"}, {"name": "target", "type": "int"}, {"name": "k", "type": "int"}],
            return_type="int[]",
            time_limit_ms=2200,
            memory_limit_mb=256,
            rating=1600,
            is_active=True,
        ),
    ),
    (
        "Maximum Sum BST in Binary Tree",
        build_max_sum_bst_cases,
        dict(
            description="Return the maximum sum of any subtree of the given binary tree that is also a valid binary search tree.",
            difficulty=Difficulty.HARD,
            input_format="Line 1: JSON array root in level-order form using null for missing children",
            output_format="Single integer: the maximum BST subtree sum",
            constraints="1 <= number of nodes <= 4 * 10^4\n-4 * 10^4 <= Node.val <= 4 * 10^4",
            method_name="maxSumBST",
            parameters=[{"name": "root", "type": "TreeNode"}],
            return_type="int",
            time_limit_ms=2200,
            memory_limit_mb=256,
            rating=1650,
            is_active=True,
        ),
    ),
    (
        "Distribute Coins in Binary Tree",
        build_distribute_coins_cases,
        dict(
            description="Each node stores some coins and the total number of coins equals the total number of nodes. One move transfers a coin between adjacent nodes. Return the minimum moves needed so every node has exactly one coin.",
            difficulty=Difficulty.HARD,
            input_format="Line 1: JSON array root in level-order form using null for missing children",
            output_format="Single integer: the minimum number of moves",
            constraints="1 <= number of nodes <= 1000\n0 <= Node.val <= number of nodes\nTotal coins equals number of nodes",
            method_name="distributeCoins",
            parameters=[{"name": "root", "type": "TreeNode"}],
            return_type="int",
            time_limit_ms=2000,
            memory_limit_mb=256,
            rating=1550,
            is_active=True,
        ),
    ),
    (
        "Maximum Product of Splitted Binary Tree",
        build_max_product_cases,
        dict(
            description="Remove exactly one edge from the binary tree to split it into two trees. Return the maximum product of the sums of the resulting two trees modulo 1e9+7.",
            difficulty=Difficulty.HARD,
            input_format="Line 1: JSON array root in level-order form using null for missing children",
            output_format="Single integer: the maximum product modulo 1000000007",
            constraints="2 <= number of nodes <= 5 * 10^4\n1 <= Node.val <= 10^4",
            method_name="maxProduct",
            parameters=[{"name": "root", "type": "TreeNode"}],
            return_type="int",
            time_limit_ms=2200,
            memory_limit_mb=256,
            rating=1600,
            is_active=True,
        ),
    ),
    (
        "Smallest String Starting From Leaf",
        build_smallest_leaf_string_cases,
        dict(
            description="Every node stores a value from 0 to 25 representing 'a' to 'z'. Return the lexicographically smallest string that starts at a leaf and ends at the root.",
            difficulty=Difficulty.HARD,
            input_format="Line 1: JSON array root in level-order form using null for missing children",
            output_format="Single lowercase string",
            constraints="1 <= number of nodes <= 8500\n0 <= Node.val <= 25",
            method_name="smallestFromLeaf",
            parameters=[{"name": "root", "type": "TreeNode"}],
            return_type="str",
            time_limit_ms=2000,
            memory_limit_mb=256,
            rating=1550,
            is_active=True,
        ),
    ),
    (
        "Vertical Order Traversal of a Binary Tree",
        build_vertical_cases,
        dict(
            description="Return the vertical order traversal of the binary tree. Nodes in the same row and column must be ordered by value.",
            difficulty=Difficulty.HARD,
            input_format="Line 1: JSON array root in level-order form using null for missing children",
            output_format="JSON matrix of columns from leftmost to rightmost",
            constraints="1 <= number of nodes <= 1000\n-1000 <= Node.val <= 1000",
            method_name="verticalTraversal",
            parameters=[{"name": "root", "type": "TreeNode"}],
            return_type="int[][]",
            time_limit_ms=2200,
            memory_limit_mb=256,
            rating=1650,
            is_active=True,
        ),
    ),
    (
        "Boundary of Binary Tree",
        build_boundary_cases,
        dict(
            description="Return the boundary of the binary tree in anti-clockwise order starting from the root: left boundary, leaves, then reversed right boundary, without duplicates.",
            difficulty=Difficulty.HARD,
            input_format="Line 1: JSON array root in level-order form using null for missing children",
            output_format="JSON array representing the boundary traversal",
            constraints="0 <= number of nodes <= 10^4\n-1000 <= Node.val <= 1000",
            method_name="boundaryOfBinaryTree",
            parameters=[{"name": "root", "type": "TreeNode"}],
            return_type="int[]",
            time_limit_ms=2200,
            memory_limit_mb=256,
            rating=1600,
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
