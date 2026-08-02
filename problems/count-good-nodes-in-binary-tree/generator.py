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


def solve(root) -> int:
    def dfs(node, mx):
        if not node:
            return 0
        good = 1 if node.val >= mx else 0
        nmx = max(mx, node.val)
        return good + dfs(node.left, nmx) + dfs(node.right, nmx)
    return dfs(root, float("-inf"))


def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    for offset in range(count):
        n = rng.randint(1, 15)
        vals = []
        for i in range(n):
            if i > 0 and rng.random() < 0.2:
                vals.append(None)
            else:
                vals.append(rng.randint(-10, 10))
        if vals[0] is None:
            vals[0] = 0
        root = build_tree(vals)
        if root is None:
            continue
        yield {
            "input": json.dumps(tree_to_list(root)),
            "expected_output": json.dumps(solve(root)),
            "order_index": start_index + offset,
            "is_sample": False,
        }
