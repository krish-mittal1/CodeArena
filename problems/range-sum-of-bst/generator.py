from __future__ import annotations
import json
import random
from collections import deque

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


def solve(root, low: int, high: int) -> int:
    if not root:
        return 0
    if root.val < low:
        return solve(root.right, low, high)
    if root.val > high:
        return solve(root.left, low, high)
    return root.val + solve(root.left, low, high) + solve(root.right, low, high)


def _insert(root, val):
    if not root:
        return TreeNode(val)
    if val < root.val:
        root.left = _insert(root.left, val)
    else:
        root.right = _insert(root.right, val)
    return root

def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    for offset in range(count):
        vals = rng.sample(range(1, 50), rng.randint(1, 15))
        root = None
        for v in vals:
            root = _insert(root, v)
        low, high = sorted(rng.sample(range(1, 50), 2))
        yield {
            "input": f"{json.dumps(tree_to_list(root))}\n{json.dumps(low)}\n{json.dumps(high)}",
            "expected_output": json.dumps(solve(root, low, high)),
            "order_index": start_index + offset,
            "is_sample": False,
        }
