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


def _same(a, b):
    if not a and not b:
        return True
    if not a or not b or a.val != b.val:
        return False
    return _same(a.left, b.left) and _same(a.right, b.right)

def solve(root, subRoot) -> bool:
    if not root:
        return False
    if _same(root, subRoot):
        return True
    return solve(root.left, subRoot) or solve(root.right, subRoot)


def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    for offset in range(count):
        vals = [rng.randint(0, 5) for _ in range(rng.randint(1, 9))]
        # sparse nulls
        root_list = vals
        if rng.random() < 0.5:
            sub = vals[rng.randint(0, len(vals) - 1):]
            # take a single-node subtree often
            sub = [vals[rng.randint(0, len(vals) - 1)]]
        else:
            sub = [rng.randint(0, 5)]
        root = build_tree(root_list)
        subRoot = build_tree(sub)
        yield {
            "input": f"{json.dumps(root_list)}\n{json.dumps(sub)}",
            "expected_output": json.dumps(solve(root, subRoot)),
            "order_index": start_index + offset,
            "is_sample": False,
        }
