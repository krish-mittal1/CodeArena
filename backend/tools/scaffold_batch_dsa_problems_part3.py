"""Problems 46–55+ for batch scaffold."""

from __future__ import annotations

from backend.tools.scaffold_batch_dsa_problems import (
    AMZN_GOOG,
    AMZN_META,
    FAANG_PLUS,
    GOOG_AMZN,
    GOOG_META,
    HEAP_HEAVY,
    HUB_NAMES,
    _companies,
    _dump_case,
    _gen_module,
)


def extend_final(P: list[dict]) -> list[dict]:
    def add(**kwargs):
        companies = kwargs.pop("companies")
        kwargs["companies"] = [c for c in companies if c in HUB_NAMES]
        P.append(kwargs)

    # 46 Surrounded Regions
    add(
        slug="surrounded-regions",
        title="Surrounded Regions",
        difficulty="medium",
        rating=1200,
        topic="Graphs",
        companies=_companies(*AMZN_GOOG, "Meta", "Uber"),
        description=(
            "Given an m x n matrix board containing 'X' and 'O', capture all regions that are 4-directionally "
            "surrounded by 'X'.\nA region is captured by flipping all 'O's into 'X's in that surrounded region.\n"
            "Board is provided as an array of strings (each string a row). Return the board after capture as string[]."
        ),
        input_format="Line 1: JSON array of strings board",
        output_format="JSON array of strings board after capture",
        constraints="m == board.length\nn == board[i].length\n1 <= m, n <= 50\nboard[i][j] is 'X' or 'O'",
        method_name="solve",
        parameters=[{"name": "board", "type": "str[]"}],
        return_type="str[]",
        samples=[
            _dump_case([["XXXX", "XOOX", "XXOX", "XOXX"]], ["XXXX", "XXXX", "XXXX", "XOXX"]),
            _dump_case([["X"]], ["X"]),
        ],
        tests=[
            _dump_case([["O"]], ["O"]),
            _dump_case([["OX", "XO"]], ["OX", "XO"]),
            _dump_case([["OO", "OO"]], ["OO", "OO"]),
        ],
        generator_count=50,
        generator_seed=21046,
        generator=_gen_module(
            '''
def solve(board: list[str]) -> list[str]:
    if not board:
        return board
    m, n = len(board), len(board[0])
    g = [list(row) for row in board]
    def dfs(i, j):
        if i < 0 or j < 0 or i >= m or j >= n or g[i][j] != "O":
            return
        g[i][j] = "S"
        dfs(i+1,j); dfs(i-1,j); dfs(i,j+1); dfs(i,j-1)
    for i in range(m):
        dfs(i, 0); dfs(i, n-1)
    for j in range(n):
        dfs(0, j); dfs(m-1, j)
    for i in range(m):
        for j in range(n):
            if g[i][j] == "O":
                g[i][j] = "X"
            elif g[i][j] == "S":
                g[i][j] = "O"
    return ["".join(row) for row in g]
''',
            '''
def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    for offset in range(count):
        m, n = rng.randint(1, 8), rng.randint(1, 8)
        board = ["".join(rng.choice("XO") for _ in range(n)) for _ in range(m)]
        yield {
            "input": json.dumps(board),
            "expected_output": json.dumps(solve(board)),
            "order_index": start_index + offset,
            "is_sample": False,
        }
''',
        ),
    )

    # 47 Course Schedule II
    add(
        slug="course-schedule-ii",
        title="Course Schedule II",
        difficulty="medium",
        rating=1200,
        topic="Graphs",
        companies=_companies(*AMZN_GOOG, "Meta", "Uber", "LinkedIn"),
        description=(
            "There are a total of numCourses courses you have to take, labeled from 0 to numCourses - 1. "
            "You are given an array prerequisites where prerequisites[i] = [ai, bi] indicates that you must "
            "take course bi first if you want to take course ai.\n"
            "Return the ordering of courses you should take to finish all courses. If there are many valid answers, "
            "return any of them. If it is impossible to finish all courses, return an empty array."
        ),
        input_format="Line 1: integer numCourses\nLine 2: JSON 2D array prerequisites",
        output_format="JSON array course order (any valid topo order)",
        constraints="1 <= numCourses <= 2000\n0 <= prerequisites.length <= numCourses * (numCourses - 1)",
        method_name="findOrder",
        parameters=[{"name": "numCourses", "type": "int"}, {"name": "prerequisites", "type": "int[][]"}],
        return_type="int[]",
        samples=[
            _dump_case([2, [[1, 0]]], [0, 1]),
            _dump_case([4, [[1, 0], [2, 0], [3, 1], [3, 2]]], [0, 1, 2, 3]),
            _dump_case([1, []], [0]),
        ],
        tests=[
            _dump_case([2, [[0, 1], [1, 0]]], []),
            _dump_case([3, [[1, 0], [1, 2], [0, 1]]], []),
            _dump_case([3, []], [0, 1, 2]),
        ],
        generator_count=60,
        generator_seed=21047,
        generator=_gen_module(
            '''
def solve(numCourses: int, prerequisites: list[list[int]]) -> list[int]:
    from collections import defaultdict, deque
    g = defaultdict(list)
    indeg = [0] * numCourses
    for a, b in prerequisites:
        g[b].append(a)
        indeg[a] += 1
    q = deque([i for i in range(numCourses) if indeg[i] == 0])
    order = []
    while q:
        u = q.popleft()
        order.append(u)
        for v in g[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                q.append(v)
    return order if len(order) == numCourses else []
''',
            '''
def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    for offset in range(count):
        n = rng.randint(1, 10)
        edges = []
        for a in range(n):
            for b in range(a):
                if rng.random() < 0.2:
                    edges.append([a, b])  # DAG-ish
        if rng.random() < 0.2 and n >= 2:
            edges.append([0, 1])
            edges.append([1, 0])
        yield {
            "input": f"{json.dumps(n)}\\n{json.dumps(edges)}",
            "expected_output": json.dumps(solve(n, edges)),
            "order_index": start_index + offset,
            "is_sample": False,
        }
''',
        ),
        # topo order may vary — use special compare later? For dry-run expected is from our BFS which is deterministic
    )

    # 48 Is Graph Bipartite
    add(
        slug="is-graph-bipartite",
        title="Is Graph Bipartite",
        difficulty="medium",
        rating=1200,
        topic="Graphs",
        companies=_companies(*GOOG_META, "Amazon", "Uber", "Microsoft"),
        description=(
            "There is an undirected graph with n nodes, where each node is numbered between 0 and n - 1. "
            "You are given a 2D array graph, where graph[u] is an array of nodes that node u is adjacent to.\n"
            "Return true if and only if it is bipartite."
        ),
        input_format="Line 1: JSON 2D array graph (adjacency list)",
        output_format="Boolean true/false",
        constraints="graph.length == n\n1 <= n <= 100\n0 <= graph[u].length < n\nNo self-edges; undirected",
        method_name="isBipartite",
        parameters=[{"name": "graph", "type": "int[][]"}],
        return_type="bool",
        samples=[
            _dump_case([[[1, 2, 3], [0, 2], [0, 1, 3], [0, 2]]], False),
            _dump_case([[[1, 3], [0, 2], [1, 3], [0, 2]]], True),
        ],
        tests=[
            _dump_case([[[]]], True),
            _dump_case([[[1], [0]]], True),
            _dump_case([[[1, 2], [0, 2], [0, 1]]], False),
        ],
        generator_count=60,
        generator_seed=21048,
        generator=_gen_module(
            '''
def solve(graph: list[list[int]]) -> bool:
    n = len(graph)
    color = [-1] * n
    for start in range(n):
        if color[start] != -1:
            continue
        color[start] = 0
        q = deque([start])
        while q:
            u = q.popleft()
            for v in graph[u]:
                if color[v] == -1:
                    color[v] = color[u] ^ 1
                    q.append(v)
                elif color[v] == color[u]:
                    return False
    return True
''',
            '''
def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    for offset in range(count):
        n = rng.randint(1, 10)
        edges = set()
        for i in range(n):
            for j in range(i + 1, n):
                if rng.random() < 0.25:
                    edges.add((i, j))
        g = [[] for _ in range(n)]
        for a, b in edges:
            g[a].append(b)
            g[b].append(a)
        yield {
            "input": json.dumps(g),
            "expected_output": json.dumps(solve(g)),
            "order_index": start_index + offset,
            "is_sample": False,
        }
''',
        ),
    )

    # 49 Network Delay Time
    add(
        slug="network-delay-time",
        title="Network Delay Time",
        difficulty="medium",
        rating=1200,
        topic="Graphs",
        companies=_companies(*AMZN_GOOG, "Meta", "Microsoft"),
        description=(
            "You are given a network of n nodes, labeled from 1 to n. You are also given times, a list of travel "
            "times as directed edges times[i] = (ui, vi, wi), where ui is the source node, vi is the target node, "
            "and wi is the time it takes for a signal to travel from source to target.\n"
            "We will send a signal from a given node k. Return the minimum time it takes for all the n nodes to "
            "receive the signal. If it is impossible for all the n nodes to receive the signal, return -1."
        ),
        input_format="Line 1: JSON 2D array times\nLine 2: integer n\nLine 3: integer k",
        output_format="Integer min time or -1",
        constraints="1 <= k <= n <= 100\n1 <= times.length <= 6000",
        method_name="networkDelayTime",
        parameters=[
            {"name": "times", "type": "int[][]"},
            {"name": "n", "type": "int"},
            {"name": "k", "type": "int"},
        ],
        return_type="int",
        samples=[
            _dump_case([[[2, 1, 1], [2, 3, 1], [3, 4, 1]], 4, 2], 2),
            _dump_case([[[1, 2, 1]], 2, 1], 1),
            _dump_case([[[1, 2, 1]], 2, 2], -1),
        ],
        tests=[
            _dump_case([[[1, 2, 1], [2, 1, 3]], 2, 2], 3),
            _dump_case([[[1, 2, 1], [2, 3, 2], [1, 3, 4]], 3, 1], 3),
        ],
        generator_count=60,
        generator_seed=21049,
        generator=_gen_module(
            '''
def solve(times: list[list[int]], n: int, k: int) -> int:
    g = [[] for _ in range(n + 1)]
    for u, v, w in times:
        g[u].append((v, w))
    dist = [10**18] * (n + 1)
    dist[k] = 0
    pq = [(0, k)]
    while pq:
        d, u = heapq.heappop(pq)
        if d != dist[u]:
            continue
        for v, w in g[u]:
            nd = d + w
            if nd < dist[v]:
                dist[v] = nd
                heapq.heappush(pq, (nd, v))
    ans = max(dist[1:])
    return -1 if ans >= 10**18 else ans
''',
            '''
def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    for offset in range(count):
        n = rng.randint(1, 8)
        times = []
        for _ in range(rng.randint(0, n * 2)):
            u, v = rng.randint(1, n), rng.randint(1, n)
            if u != v:
                times.append([u, v, rng.randint(1, 20)])
        k = rng.randint(1, n)
        yield {
            "input": f"{json.dumps(times)}\\n{json.dumps(n)}\\n{json.dumps(k)}",
            "expected_output": json.dumps(solve(times, n, k)),
            "order_index": start_index + offset,
            "is_sample": False,
        }
''',
        ),
    )

    # 50 Last Stone Weight
    add(
        slug="last-stone-weight",
        title="Last Stone Weight",
        difficulty="easy",
        rating=900,
        topic="Heap",
        companies=_companies(*HEAP_HEAVY, "Apple"),
        description=(
            "You are given an array of integers stones where stones[i] is the weight of the ith stone.\n"
            "We are playing a game with the stones. On each turn, we choose the heaviest two stones and smash them together. "
            "Suppose the heaviest two stones have weights x and y with x <= y. The result of this smash is: "
            "If x == y, both stones are destroyed; if x != y, x is destroyed and y has new weight y - x.\n"
            "At the end of the game, there is at most one stone left. Return the weight of the last remaining stone. "
            "If there are no stones left, return 0."
        ),
        input_format="Line 1: JSON array stones",
        output_format="Integer last stone weight",
        constraints="1 <= stones.length <= 30\n1 <= stones[i] <= 1000",
        method_name="lastStoneWeight",
        parameters=[{"name": "stones", "type": "int[]"}],
        return_type="int",
        samples=[
            _dump_case([[2, 7, 4, 1, 8, 1]], 1),
            _dump_case([[1]], 1),
        ],
        tests=[
            _dump_case([[1, 1]], 0),
            _dump_case([[10, 4, 2, 3]], 1),
            _dump_case([[9, 3, 2, 10]], 0),
        ],
        generator_count=80,
        generator_seed=21050,
        generator=_gen_module(
            '''
def solve(stones: list[int]) -> int:
    h = [-s for s in stones]
    heapq.heapify(h)
    while len(h) > 1:
        y = -heapq.heappop(h)
        x = -heapq.heappop(h)
        if y != x:
            heapq.heappush(h, -(y - x))
    return -h[0] if h else 0
''',
            '''
def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    for offset in range(count):
        stones = [rng.randint(1, 100) for _ in range(rng.randint(1, 20))]
        yield {
            "input": json.dumps(stones),
            "expected_output": json.dumps(solve(stones)),
            "order_index": start_index + offset,
            "is_sample": False,
        }
''',
        ),
    )

    # 51 K Closest Points
    add(
        slug="k-closest-points-to-origin",
        title="K Closest Points to Origin",
        difficulty="medium",
        rating=1100,
        topic="Heap",
        companies=_companies(*AMZN_META, "Google", "Uber", "LinkedIn"),
        description=(
            "Given an array of points where points[i] = [xi, yi] represents a point on the X-Y plane and an integer k, "
            "return the k closest points to the origin (0, 0).\n"
            "The distance between two points on the X-Y plane is the Euclidean distance.\n"
            "You may return the answer in any order. The answer is guaranteed to be unique (except for the order that it is in)."
        ),
        input_format="Line 1: JSON 2D array points\nLine 2: integer k",
        output_format="JSON 2D array of k closest points",
        constraints="1 <= k <= points.length <= 10^4\n-10^4 <= xi, yi <= 10^4",
        method_name="kClosest",
        parameters=[{"name": "points", "type": "int[][]"}, {"name": "k", "type": "int"}],
        return_type="int[][]",
        samples=[
            _dump_case([[[1, 3], [-2, 2]], 1], [[-2, 2]]),
            _dump_case([[[3, 3], [5, -1], [-2, 4]], 2], [[3, 3], [-2, 4]]),
        ],
        tests=[
            _dump_case([[[0, 1]], 1], [[0, 1]]),
            _dump_case([[[1, 0], [0, 1]], 2], [[1, 0], [0, 1]]),
        ],
        generator_count=60,
        generator_seed=21051,
        generator=_gen_module(
            '''
def solve(points: list[list[int]], k: int) -> list[list[int]]:
    return heapq.nsmallest(k, points, key=lambda p: p[0]*p[0] + p[1]*p[1])
''',
            '''
def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    for offset in range(count):
        n = rng.randint(1, 20)
        # unique distances
        points = []
        used = set()
        while len(points) < n:
            x, y = rng.randint(-20, 20), rng.randint(-20, 20)
            d = x*x + y*y
            if d in used:
                continue
            used.add(d)
            points.append([x, y])
        k = rng.randint(1, n)
        yield {
            "input": f"{json.dumps(points)}\\n{json.dumps(k)}",
            "expected_output": json.dumps(solve(points, k)),
            "order_index": start_index + offset,
            "is_sample": False,
        }
''',
        ),
        sort_output=True,
    )

    # 52 Reorganize String
    add(
        slug="reorganize-string",
        title="Reorganize String",
        difficulty="medium",
        rating=1150,
        topic="Heap",
        companies=_companies(*AMZN_GOOG, "Meta", "Uber"),
        description=(
            "Given a string s, rearrange the characters of s so that any two adjacent characters are not the same.\n"
            "Return any possible rearrangement of s or return \"\" if not possible."
        ),
        input_format="Line 1: string s",
        output_format="String rearranged or empty string",
        constraints="1 <= s.length <= 500\ns consists of lowercase English letters.",
        method_name="reorganizeString",
        parameters=[{"name": "s", "type": "str"}],
        return_type="str",
        samples=[
            _dump_case(["aab"], "aba"),
            _dump_case(["aaab"], ""),
        ],
        tests=[
            _dump_case(["a"], "a"),
            _dump_case(["aa"], ""),
            _dump_case(["vvvlo"], "vlvov"),
        ],
        generator_count=60,
        generator_seed=21052,
        generator=_gen_module(
            '''
def solve(s: str) -> str:
    cnt = Counter(s)
    heap = [(-c, ch) for ch, c in cnt.items()]
    heapq.heapify(heap)
    res = []
    prev = None
    while heap:
        c, ch = heapq.heappop(heap)
        res.append(ch)
        if prev:
            heapq.heappush(heap, prev)
        c += 1
        prev = (c, ch) if c < 0 else None
    ans = "".join(res)
    return ans if len(ans) == len(s) else ""
''',
            '''
def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    letters = "abcde"
    for offset in range(count):
        s = "".join(rng.choice(letters) for _ in range(rng.randint(1, 20)))
        yield {
            "input": json.dumps(s),
            "expected_output": json.dumps(solve(s)),
            "order_index": start_index + offset,
            "is_sample": False,
        }
''',
        ),
        # multiple valid rearrangements — judge uses exact match from our deterministic solver
    )

    # 53 Asteroid Collision
    add(
        slug="asteroid-collision",
        title="Asteroid Collision",
        difficulty="medium",
        rating=1150,
        topic="Stack",
        companies=_companies(*AMZN_META, "Google", "Uber", "LinkedIn"),
        description=(
            "We are given an array asteroids of integers representing asteroids in a row.\n"
            "For each asteroid, the absolute value represents its size, and the sign represents its direction "
            "(positive meaning right, negative meaning left). Each asteroid moves at the same speed.\n"
            "Find out the state of the asteroids after all collisions. If two asteroids meet, the smaller one will explode. "
            "If both are the same size, both will explode. Two asteroids moving in the same direction will never meet."
        ),
        input_format="Line 1: JSON array asteroids",
        output_format="JSON array remaining asteroids",
        constraints="2 <= asteroids.length <= 10^4\n-1000 <= asteroids[i] <= 1000\nasteroids[i] != 0",
        method_name="asteroidCollision",
        parameters=[{"name": "asteroids", "type": "int[]"}],
        return_type="int[]",
        samples=[
            _dump_case([[5, 10, -5]], [5, 10]),
            _dump_case([[8, -8]], []),
            _dump_case([[10, 2, -5]], [10]),
        ],
        tests=[
            _dump_case([[-2, -1, 1, 2]], [-2, -1, 1, 2]),
            _dump_case([[-2, 1, -1, -2]], [-2, -2]),
            _dump_case([[1, -1, -2, -2]], [-2, -2]),
        ],
        generator_count=80,
        generator_seed=21053,
        generator=_gen_module(
            '''
def solve(asteroids: list[int]) -> list[int]:
    stack = []
    for a in asteroids:
        alive = True
        while alive and a < 0 and stack and stack[-1] > 0:
            if stack[-1] < -a:
                stack.pop()
                continue
            elif stack[-1] == -a:
                stack.pop()
            alive = False
        if alive:
            stack.append(a)
    return stack
''',
            '''
def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    for offset in range(count):
        n = rng.randint(2, 25)
        asteroids = []
        for _ in range(n):
            v = rng.randint(1, 20)
            asteroids.append(v if rng.random() < 0.5 else -v)
        yield {
            "input": json.dumps(asteroids),
            "expected_output": json.dumps(solve(asteroids)),
            "order_index": start_index + offset,
            "is_sample": False,
        }
''',
        ),
    )

    # 54 Find Peak Element
    add(
        slug="find-peak-element",
        title="Find Peak Element",
        difficulty="medium",
        rating=1100,
        topic="Binary Search",
        companies=_companies(*GOOG_META, "Amazon", "Microsoft", "Apple"),
        description=(
            "A peak element is an element that is strictly greater than its neighbors.\n"
            "Given a 0-indexed integer array nums, find a peak element, and return its index. "
            "If the array contains multiple peaks, return the index to any of the peaks.\n"
            "You may imagine that nums[-1] = nums[n] = -∞.\n"
            "You must write an algorithm that runs in O(log n) time."
        ),
        input_format="Line 1: JSON array nums",
        output_format="Integer peak index",
        constraints="1 <= nums.length <= 1000\n-2^31 <= nums[i] <= 2^31 - 1\nnums[i] != nums[i + 1] for all valid i",
        method_name="findPeakElement",
        parameters=[{"name": "nums", "type": "int[]"}],
        return_type="int",
        samples=[
            _dump_case([[1, 2, 3, 1]], 2),
            _dump_case([[1, 2, 1, 3, 5, 6, 4]], 5),
        ],
        tests=[
            _dump_case([[1]], 0),
            _dump_case([[1, 2]], 1),
            _dump_case([[2, 1]], 0),
            _dump_case([[3, 2, 1]], 0),
        ],
        generator_count=80,
        generator_seed=21054,
        generator=_gen_module(
            '''
def solve(nums: list[int]) -> int:
    lo, hi = 0, len(nums) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if nums[mid] < nums[mid + 1]:
            lo = mid + 1
        else:
            hi = mid
    return lo
''',
            '''
def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    for offset in range(count):
        n = rng.randint(1, 30)
        nums = [rng.randint(-50, 50)]
        for _ in range(n - 1):
            nxt = rng.randint(-50, 50)
            while nxt == nums[-1]:
                nxt = rng.randint(-50, 50)
            nums.append(nxt)
        yield {
            "input": json.dumps(nums),
            "expected_output": json.dumps(solve(nums)),
            "order_index": start_index + offset,
            "is_sample": False,
        }
''',
        ),
    )

    # 55 Combination Sum IV
    add(
        slug="combination-sum-iv",
        title="Combination Sum IV",
        difficulty="medium",
        rating=1200,
        topic="Dynamic Programming",
        companies=_companies(*AMZN_GOOG, "Meta", "Uber"),
        description=(
            "Given an array of distinct integers nums and a target integer target, return the number of possible "
            "combinations that add up to target.\nThe test cases are generated so that the answer can fit in a 32-bit integer.\n"
            "Note that different sequences are counted as different combinations."
        ),
        input_format="Line 1: JSON array nums\nLine 2: integer target",
        output_format="Integer number of combinations",
        constraints="1 <= nums.length <= 200\n1 <= nums[i] <= 1000\nAll elements are unique.\n1 <= target <= 1000",
        method_name="combinationSum4",
        parameters=[{"name": "nums", "type": "int[]"}, {"name": "target", "type": "int"}],
        return_type="int",
        samples=[
            _dump_case([[1, 2, 3], 4], 7),
            _dump_case([[9], 3], 0),
        ],
        tests=[
            _dump_case([[1], 1], 1),
            _dump_case([[1, 2], 3], 3),
            _dump_case([[3, 1, 2], 4], 7),
        ],
        generator_count=60,
        generator_seed=21055,
        generator=_gen_module(
            '''
def solve(nums: list[int], target: int) -> int:
    dp = [0] * (target + 1)
    dp[0] = 1
    for t in range(1, target + 1):
        for x in nums:
            if x <= t:
                dp[t] += dp[t - x]
    return dp[target]
''',
            '''
def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    for offset in range(count):
        nums = sorted({rng.randint(1, 15) for _ in range(rng.randint(1, 6))})
        target = rng.randint(1, 40)
        yield {
            "input": f"{json.dumps(nums)}\\n{json.dumps(target)}",
            "expected_output": json.dumps(solve(nums, target)),
            "order_index": start_index + offset,
            "is_sample": False,
        }
''',
        ),
    )

    # 56 Perfect Squares
    add(
        slug="perfect-squares",
        title="Perfect Squares",
        difficulty="medium",
        rating=1200,
        topic="Dynamic Programming",
        companies=_companies(*GOOG_AMZN, "Meta", "Microsoft", "Uber"),
        description=(
            "Given an integer n, return the least number of perfect square numbers that sum to n.\n"
            "A perfect square is an integer that is the square of an integer."
        ),
        input_format="Line 1: integer n",
        output_format="Integer least count",
        constraints="1 <= n <= 10^4",
        method_name="numSquares",
        parameters=[{"name": "n", "type": "int"}],
        return_type="int",
        samples=[
            _dump_case([12], 3),
            _dump_case([13], 2),
        ],
        tests=[
            _dump_case([1], 1),
            _dump_case([4], 1),
            _dump_case([7], 4),
            _dump_case([100], 1),
        ],
        generator_count=60,
        generator_seed=21056,
        generator=_gen_module(
            '''
def solve(n: int) -> int:
    dp = [0] + [10**9] * n
    for i in range(1, n + 1):
        j = 1
        while j * j <= i:
            dp[i] = min(dp[i], dp[i - j * j] + 1)
            j += 1
    return dp[n]
''',
            '''
def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    for offset in range(count):
        n = rng.randint(1, 200)
        yield {
            "input": json.dumps(n),
            "expected_output": json.dumps(solve(n)),
            "order_index": start_index + offset,
            "is_sample": False,
        }
''',
        ),
    )

    # 57 Triangle
    add(
        slug="triangle",
        title="Triangle",
        difficulty="medium",
        rating=1150,
        topic="Dynamic Programming",
        companies=_companies(*AMZN_GOOG, "Meta", "Apple"),
        description=(
            "Given a triangle array, return the minimum path sum from top to bottom.\n"
            "For each step, you may move to an adjacent number of the row below. "
            "More formally, if you are on index i on the current row, you may move to either index i or index i + 1 on the next row."
        ),
        input_format="Line 1: JSON 2D array triangle",
        output_format="Integer minimum path sum",
        constraints="1 <= triangle.length <= 200\ntriangle[0].length == 1\ntriangle[i].length == triangle[i - 1].length + 1\n-10^4 <= triangle[i][j] <= 10^4",
        method_name="minimumTotal",
        parameters=[{"name": "triangle", "type": "int[][]"}],
        return_type="int",
        samples=[
            _dump_case([[[2], [3, 4], [6, 5, 7], [4, 1, 8, 3]]], 11),
            _dump_case([[[-10]]], -10),
        ],
        tests=[
            _dump_case([[[1], [2, 3]]], 3),
            _dump_case([[[1], [-1, -2], [1, 2, 3]]], 0),
        ],
        generator_count=50,
        generator_seed=21057,
        generator=_gen_module(
            '''
def solve(triangle: list[list[int]]) -> int:
    dp = triangle[-1][:]
    for r in range(len(triangle) - 2, -1, -1):
        for c in range(len(triangle[r])):
            dp[c] = triangle[r][c] + min(dp[c], dp[c + 1])
    return dp[0]
''',
            '''
def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    for offset in range(count):
        rows = rng.randint(1, 10)
        triangle = [[rng.randint(-20, 20) for _ in range(r + 1)] for r in range(rows)]
        yield {
            "input": json.dumps(triangle),
            "expected_output": json.dumps(solve(triangle)),
            "order_index": start_index + offset,
            "is_sample": False,
        }
''',
        ),
    )

    # 58 Fibonacci Number
    add(
        slug="fibonacci-number",
        title="Fibonacci Number",
        difficulty="easy",
        rating=800,
        topic="Dynamic Programming",
        companies=_companies(*FAANG_PLUS, "Apple"),
        description=(
            "The Fibonacci numbers, commonly denoted F(n) form a sequence, called the Fibonacci sequence, "
            "such that each number is the sum of the two preceding ones, starting from 0 and 1. That is, "
            "F(0) = 0, F(1) = 1, F(n) = F(n - 1) + F(n - 2) for n > 1.\nGiven n, calculate F(n)."
        ),
        input_format="Line 1: integer n",
        output_format="Integer F(n)",
        constraints="0 <= n <= 30",
        method_name="fib",
        parameters=[{"name": "n", "type": "int"}],
        return_type="int",
        samples=[
            _dump_case([2], 1),
            _dump_case([3], 2),
            _dump_case([4], 3),
        ],
        tests=[
            _dump_case([0], 0),
            _dump_case([1], 1),
            _dump_case([10], 55),
            _dump_case([30], 832040),
        ],
        generator_count=31,
        generator_seed=21058,
        generator=_gen_module(
            '''
def solve(n: int) -> int:
    if n < 2:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b
''',
            '''
def generate_cases(*, count: int, seed: int, start_index: int):
    for offset, n in enumerate(range(0, min(count, 31))):
        yield {
            "input": json.dumps(n),
            "expected_output": json.dumps(solve(n)),
            "order_index": start_index + offset,
            "is_sample": False,
        }
''',
        ),
    )

    # 59 Power of Two
    add(
        slug="power-of-two",
        title="Power of Two",
        difficulty="easy",
        rating=800,
        topic="Bit Manipulation",
        companies=_companies(*FAANG_PLUS, "Apple"),
        description="Given an integer n, return true if it is a power of two. Otherwise, return false.\nAn integer n is a power of two, if there exists an integer x such that n == 2^x.",
        input_format="Line 1: integer n",
        output_format="Boolean true/false",
        constraints="-2^31 <= n <= 2^31 - 1",
        method_name="isPowerOfTwo",
        parameters=[{"name": "n", "type": "int"}],
        return_type="bool",
        samples=[
            _dump_case([1], True),
            _dump_case([16], True),
            _dump_case([3], False),
        ],
        tests=[
            _dump_case([0], False),
            _dump_case([-2], False),
            _dump_case([1024], True),
            _dump_case([2**30], True),
        ],
        generator_count=60,
        generator_seed=21059,
        generator=_gen_module(
            '''
def solve(n: int) -> bool:
    return n > 0 and (n & (n - 1)) == 0
''',
            '''
def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    for offset in range(count):
        if rng.random() < 0.4:
            n = 1 << rng.randint(0, 30)
        else:
            n = rng.randint(-100, 10**6)
        yield {
            "input": json.dumps(n),
            "expected_output": json.dumps(solve(n)),
            "order_index": start_index + offset,
            "is_sample": False,
        }
''',
        ),
    )

    # 60 Intersection of Two Arrays
    add(
        slug="intersection-of-two-arrays",
        title="Intersection of Two Arrays",
        difficulty="easy",
        rating=850,
        topic="Hash Map",
        companies=_companies(*AMZN_META, "Google", "Apple", "Uber"),
        description=(
            "Given two integer arrays nums1 and nums2, return an array of their intersection. "
            "Each element in the result must be unique and you may return the result in any order."
        ),
        input_format="Line 1: JSON array nums1\nLine 2: JSON array nums2",
        output_format="JSON array of unique intersection",
        constraints="1 <= nums1.length, nums2.length <= 1000\n0 <= nums1[i], nums2[i] <= 1000",
        method_name="intersection",
        parameters=[{"name": "nums1", "type": "int[]"}, {"name": "nums2", "type": "int[]"}],
        return_type="int[]",
        samples=[
            _dump_case([[1, 2, 2, 1], [2, 2]], [2]),
            _dump_case([[4, 9, 5], [9, 4, 9, 8, 4]], [9, 4]),
        ],
        tests=[
            _dump_case([[1], [1]], [1]),
            _dump_case([[1, 2], [3, 4]], []),
        ],
        generator_count=60,
        generator_seed=21060,
        generator=_gen_module(
            '''
def solve(nums1: list[int], nums2: list[int]) -> list[int]:
    return list(set(nums1) & set(nums2))
''',
            '''
def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    for offset in range(count):
        a = [rng.randint(0, 30) for _ in range(rng.randint(1, 20))]
        b = [rng.randint(0, 30) for _ in range(rng.randint(1, 20))]
        yield {
            "input": f"{json.dumps(a)}\\n{json.dumps(b)}",
            "expected_output": json.dumps(solve(a, b)),
            "order_index": start_index + offset,
            "is_sample": False,
        }
''',
        ),
        sort_output=True,
    )

    # 61 Remove Duplicates from Sorted Array
    add(
        slug="remove-duplicates-from-sorted-array",
        title="Remove Duplicates from Sorted Array",
        difficulty="easy",
        rating=850,
        topic="Two Pointers",
        companies=_companies(*FAANG_PLUS, "Adobe"),
        description=(
            "Given an integer array nums sorted in non-decreasing order, remove the duplicates in-place such that "
            "each unique element appears only once. The relative order of the elements should be kept the same.\n"
            "Return k after placing the final result in the first k slots of nums. "
            "For this platform, return the list of unique values in order (first k elements)."
        ),
        input_format="Line 1: JSON array nums (sorted)",
        output_format="JSON array of unique values in order",
        constraints="1 <= nums.length <= 3*10^4\n-100 <= nums[i] <= 100\nnums is sorted in non-decreasing order.",
        method_name="removeDuplicates",
        parameters=[{"name": "nums", "type": "int[]"}],
        return_type="int[]",
        samples=[
            _dump_case([[1, 1, 2]], [1, 2]),
            _dump_case([[0, 0, 1, 1, 1, 2, 2, 3, 3, 4]], [0, 1, 2, 3, 4]),
        ],
        tests=[
            _dump_case([[1]], [1]),
            _dump_case([[1, 1, 1]], [1]),
            _dump_case([[-1, 0, 0, 0, 3, 3]], [-1, 0, 3]),
        ],
        generator_count=80,
        generator_seed=21061,
        generator=_gen_module(
            '''
def solve(nums: list[int]) -> list[int]:
    if not nums:
        return []
    w = 1
    for i in range(1, len(nums)):
        if nums[i] != nums[w - 1]:
            nums[w] = nums[i]
            w += 1
    return nums[:w]
''',
            '''
def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    for offset in range(count):
        n = rng.randint(1, 40)
        nums = sorted(rng.randint(-20, 20) for _ in range(n))
        yield {
            "input": json.dumps(nums),
            "expected_output": json.dumps(solve(nums[:])),
            "order_index": start_index + offset,
            "is_sample": False,
        }
''',
        ),
    )

    # 62 Search a 2D Matrix II
    add(
        slug="search-a-2d-matrix-ii",
        title="Search a 2D Matrix II",
        difficulty="medium",
        rating=1200,
        topic="Binary Search",
        companies=_companies(*AMZN_GOOG, "Meta", "Microsoft", "Apple"),
        description=(
            "Write an efficient algorithm that searches for a value target in an m x n integer matrix matrix. "
            "This matrix has the following properties: Integers in each row are sorted in ascending from left to right. "
            "Integers in each column are sorted in ascending from top to bottom."
        ),
        input_format="Line 1: JSON 2D array matrix\nLine 2: integer target",
        output_format="Boolean true/false",
        constraints="m == matrix.length\nn == matrix[i].length\n1 <= n, m <= 300\n-10^9 <= matrix[i][j] <= 10^9",
        method_name="searchMatrix",
        parameters=[{"name": "matrix", "type": "int[][]"}, {"name": "target", "type": "int"}],
        return_type="bool",
        samples=[
            _dump_case([[[1, 4, 7, 11, 15], [2, 5, 8, 12, 19], [3, 6, 9, 16, 22], [10, 13, 14, 17, 24], [18, 21, 23, 26, 30]], 5], True),
            _dump_case([[[1, 4, 7, 11, 15], [2, 5, 8, 12, 19], [3, 6, 9, 16, 22], [10, 13, 14, 17, 24], [18, 21, 23, 26, 30]], 20], False),
        ],
        tests=[
            _dump_case([[[-5]], -5], True),
            _dump_case([[[1, 2], [3, 4]], 0], False),
            _dump_case([[[1, 3, 5]], 3], True),
        ],
        generator_count=50,
        generator_seed=21062,
        generator=_gen_module(
            '''
def solve(matrix: list[list[int]], target: int) -> bool:
    if not matrix or not matrix[0]:
        return False
    m, n = len(matrix), len(matrix[0])
    r, c = 0, n - 1
    while r < m and c >= 0:
        if matrix[r][c] == target:
            return True
        if matrix[r][c] > target:
            c -= 1
        else:
            r += 1
    return False
''',
            '''
def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    for offset in range(count):
        m, n = rng.randint(1, 8), rng.randint(1, 8)
        vals = sorted(rng.sample(range(-50, 100), m * n))
        matrix = [vals[i*n:(i+1)*n] for i in range(m)]
        # enforce column sorted by regenerating carefully
        matrix = []
        base = [rng.randint(-20, 20) for _ in range(n)]
        base.sort()
        prev = base
        matrix.append(prev[:])
        for _ in range(m - 1):
            row = [prev[j] + rng.randint(0, 5) for j in range(n)]
            for j in range(1, n):
                row[j] = max(row[j], row[j-1] + 1)
            matrix.append(row)
            prev = row
        target = rng.randint(-30, 80)
        yield {
            "input": f"{json.dumps(matrix)}\\n{json.dumps(target)}",
            "expected_output": json.dumps(solve(matrix, target)),
            "order_index": start_index + offset,
            "is_sample": False,
        }
''',
        ),
    )

    return P
