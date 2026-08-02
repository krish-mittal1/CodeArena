"""Additional problem specs for scaffold_batch_dsa_problems."""

from __future__ import annotations

import json

from backend.tools.scaffold_batch_dsa_problems import (
    AMZN_GOOG,
    AMZN_META,
    APPLE_AMZN,
    FAANG,
    FAANG_PLUS,
    GOOG_AMZN,
    GOOG_META,
    HEAP_HEAVY,
    HUB_NAMES,
    META_APPLE,
    _companies,
    _dump_case,
    _gen_module,
)


def extend_more(P: list[dict]) -> list[dict]:
    def add(**kwargs):
        companies = kwargs.pop("companies")
        kwargs["companies"] = [c for c in companies if c in HUB_NAMES]
        P.append(kwargs)

    # 19 Min Cost Climbing Stairs
    add(
        slug="min-cost-climbing-stairs",
        title="Min Cost Climbing Stairs",
        difficulty="easy",
        rating=900,
        topic="Dynamic Programming",
        companies=_companies(*AMZN_GOOG, "Apple"),
        description=(
            "You are given an integer array cost where cost[i] is the cost of ith step on a staircase. "
            "Once you pay the cost, you can either climb one or two steps.\n"
            "You can either start from the step with index 0, or the step with index 1.\n"
            "Return the minimum cost to reach the top of the floor."
        ),
        input_format="Line 1: JSON array cost",
        output_format="Integer minimum cost",
        constraints="2 <= cost.length <= 1000\n0 <= cost[i] <= 999",
        method_name="minCostClimbingStairs",
        parameters=[{"name": "cost", "type": "int[]"}],
        return_type="int",
        samples=[
            _dump_case([[10, 15, 20]], 15),
            _dump_case([[1, 100, 1, 1, 1, 100, 1, 1, 100, 1]], 6),
        ],
        tests=[
            _dump_case([[0, 0]], 0),
            _dump_case([[1, 100]], 1),
            _dump_case([[0, 2, 2, 1]], 2),
        ],
        generator_count=100,
        generator_seed=21019,
        generator=_gen_module(
            '''
def solve(cost: list[int]) -> int:
    a = b = 0
    for c in reversed(cost):
        a, b = c + min(a, b), a
    return min(a, b)
''',
            '''
def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    for offset in range(count):
        n = rng.randint(2, 40)
        cost = [rng.randint(0, 100) for _ in range(n)]
        yield {
            "input": json.dumps(cost),
            "expected_output": json.dumps(solve(cost)),
            "order_index": start_index + offset,
            "is_sample": False,
        }
''',
        ),
    )

    # 20 Unique Paths II
    add(
        slug="unique-paths-ii",
        title="Unique Paths II",
        difficulty="medium",
        rating=1150,
        topic="Dynamic Programming",
        companies=_companies(*AMZN_GOOG, "Meta", "Apple"),
        description=(
            "You are given an m x n integer array obstacleGrid. There is a robot initially located at the "
            "top-left corner (0, 0). The robot tries to move to the bottom-right corner. The robot can only "
            "move either down or right at any point in time.\n"
            "An obstacle and space are marked as 1 or 0 respectively in obstacleGrid. A path that the robot "
            "takes cannot include any square that is an obstacle.\n"
            "Return the number of possible unique paths that the robot can take to reach the bottom-right corner."
        ),
        input_format="Line 1: JSON 2D array obstacleGrid",
        output_format="Integer number of paths",
        constraints="m == obstacleGrid.length\nn == obstacleGrid[i].length\n1 <= m, n <= 100\nobstacleGrid[i][j] is 0 or 1",
        method_name="uniquePathsWithObstacles",
        parameters=[{"name": "obstacleGrid", "type": "int[][]"}],
        return_type="int",
        samples=[
            _dump_case([[[0, 0, 0], [0, 1, 0], [0, 0, 0]]], 2),
            _dump_case([[[0, 1], [0, 0]]], 1),
        ],
        tests=[
            _dump_case([[[1]]], 0),
            _dump_case([[[0]]], 1),
            _dump_case([[[0, 0], [1, 1], [0, 0]]], 0),
        ],
        generator_count=80,
        generator_seed=21020,
        generator=_gen_module(
            '''
def solve(obstacleGrid: list[list[int]]) -> int:
    m, n = len(obstacleGrid), len(obstacleGrid[0])
    if obstacleGrid[0][0] == 1 or obstacleGrid[m-1][n-1] == 1:
        return 0
    dp = [0] * n
    dp[0] = 1
    for i in range(m):
        for j in range(n):
            if obstacleGrid[i][j] == 1:
                dp[j] = 0
            elif j > 0:
                dp[j] += dp[j - 1]
    return dp[-1]
''',
            '''
def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    for offset in range(count):
        m, n = rng.randint(1, 8), rng.randint(1, 8)
        grid = [[1 if rng.random() < 0.15 else 0 for _ in range(n)] for _ in range(m)]
        grid[0][0] = 0
        grid[m-1][n-1] = 0
        yield {
            "input": json.dumps(grid),
            "expected_output": json.dumps(solve(grid)),
            "order_index": start_index + offset,
            "is_sample": False,
        }
''',
        ),
    )

    # 21 Partition Equal Subset Sum
    add(
        slug="partition-equal-subset-sum",
        title="Partition Equal Subset Sum",
        difficulty="medium",
        rating=1200,
        topic="Dynamic Programming",
        companies=_companies(*AMZN_META, "Google", "Uber"),
        description=(
            "Given an integer array nums, return true if you can partition the array into two subsets such that "
            "the sum of the elements in both subsets is equal or false otherwise."
        ),
        input_format="Line 1: JSON array nums",
        output_format="Boolean true/false",
        constraints="1 <= nums.length <= 200\n1 <= nums[i] <= 100",
        method_name="canPartition",
        parameters=[{"name": "nums", "type": "int[]"}],
        return_type="bool",
        samples=[
            _dump_case([[1, 5, 11, 5]], True),
            _dump_case([[1, 2, 3, 5]], False),
        ],
        tests=[
            _dump_case([[1]], False),
            _dump_case([[1, 1]], True),
            _dump_case([[2, 2, 3, 5]], False),
            _dump_case([[1, 2, 5]], False),
        ],
        generator_count=80,
        generator_seed=21021,
        generator=_gen_module(
            '''
def solve(nums: list[int]) -> bool:
    s = sum(nums)
    if s % 2:
        return False
    target = s // 2
    dp = 1
    for x in nums:
        dp |= dp << x
    return bool(dp & (1 << target))
''',
            '''
def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    for offset in range(count):
        n = rng.randint(1, 20)
        nums = [rng.randint(1, 30) for _ in range(n)]
        yield {
            "input": json.dumps(nums),
            "expected_output": json.dumps(solve(nums)),
            "order_index": start_index + offset,
            "is_sample": False,
        }
''',
        ),
    )

    # 22 Coin Change II
    add(
        slug="coin-change-ii",
        title="Coin Change II",
        difficulty="medium",
        rating=1200,
        topic="Dynamic Programming",
        companies=_companies(*AMZN_GOOG, "Meta", "Uber"),
        description=(
            "You are given an integer array coins representing coins of different denominations and an integer "
            "amount representing a total amount of money.\n"
            "Return the number of combinations that make up that amount. If that amount of money cannot be made "
            "up by any combination of the coins, return 0.\n"
            "You may assume that you have an infinite number of each kind of coin.\n"
            "The answer is guaranteed to fit into a signed 32-bit integer."
        ),
        input_format="Line 1: integer amount\nLine 2: JSON array coins",
        output_format="Integer number of combinations",
        constraints="1 <= coins.length <= 300\n1 <= coins[i] <= 5000\n0 <= amount <= 5000",
        method_name="change",
        parameters=[{"name": "amount", "type": "int"}, {"name": "coins", "type": "int[]"}],
        return_type="int",
        samples=[
            _dump_case([5, [1, 2, 5]], 4),
            _dump_case([3, [2]], 0),
            _dump_case([10, [10]], 1),
        ],
        tests=[
            _dump_case([0, [1, 2]], 1),
            _dump_case([4, [1, 2, 3]], 4),
        ],
        generator_count=80,
        generator_seed=21022,
        generator=_gen_module(
            '''
def solve(amount: int, coins: list[int]) -> int:
    dp = [0] * (amount + 1)
    dp[0] = 1
    for c in coins:
        for a in range(c, amount + 1):
            dp[a] += dp[a - c]
    return dp[amount]
''',
            '''
def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    for offset in range(count):
        coins = sorted({rng.randint(1, 20) for _ in range(rng.randint(1, 5))})
        amount = rng.randint(0, 80)
        yield {
            "input": f"{json.dumps(amount)}\\n{json.dumps(coins)}",
            "expected_output": json.dumps(solve(amount, coins)),
            "order_index": start_index + offset,
            "is_sample": False,
        }
''',
        ),
    )

    # 23 Edit Distance
    add(
        slug="edit-distance",
        title="Edit Distance",
        difficulty="hard",
        rating=1450,
        topic="Dynamic Programming",
        companies=_companies(*GOOG_AMZN, "Meta", "Microsoft", "LinkedIn"),
        description=(
            "Given two strings word1 and word2, return the minimum number of operations required to convert "
            "word1 to word2.\nYou have the following three operations permitted on a word: Insert a character, "
            "Delete a character, Replace a character."
        ),
        input_format="Line 1: string word1\nLine 2: string word2",
        output_format="Integer edit distance",
        constraints="0 <= word1.length, word2.length <= 500\nword1 and word2 consist of lowercase English letters.",
        method_name="minDistance",
        parameters=[{"name": "word1", "type": "str"}, {"name": "word2", "type": "str"}],
        return_type="int",
        samples=[
            _dump_case(["horse", "ros"], 3),
            _dump_case(["intention", "execution"], 5),
        ],
        tests=[
            _dump_case(["", ""], 0),
            _dump_case(["a", ""], 1),
            _dump_case(["", "abc"], 3),
            _dump_case(["abc", "abc"], 0),
            _dump_case(["park", "spake"], 3),
        ],
        generator_count=60,
        generator_seed=21023,
        generator=_gen_module(
            '''
def solve(word1: str, word2: str) -> int:
    m, n = len(word1), len(word2)
    dp = list(range(n + 1))
    for i in range(1, m + 1):
        prev = dp[0]
        dp[0] = i
        for j in range(1, n + 1):
            tmp = dp[j]
            if word1[i - 1] == word2[j - 1]:
                dp[j] = prev
            else:
                dp[j] = 1 + min(prev, dp[j], dp[j - 1])
            prev = tmp
    return dp[n]
''',
            '''
def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    letters = "abcd"
    for offset in range(count):
        a = "".join(rng.choice(letters) for _ in range(rng.randint(0, 12)))
        b = "".join(rng.choice(letters) for _ in range(rng.randint(0, 12)))
        yield {
            "input": f"{json.dumps(a)}\\n{json.dumps(b)}",
            "expected_output": json.dumps(solve(a, b)),
            "order_index": start_index + offset,
            "is_sample": False,
        }
''',
        ),
    )

    # 24 Rotate Image
    add(
        slug="rotate-image",
        title="Rotate Image",
        difficulty="medium",
        rating=1100,
        topic="Matrix",
        companies=_companies(*FAANG_PLUS),
        description=(
            "You are given an n x n 2D matrix representing an image, rotate the image by 90 degrees (clockwise).\n"
            "You have to rotate the image in-place, which means you have to modify the input 2D matrix directly. "
            "DO NOT allocate another 2D matrix and do the rotation.\n"
            "Return the rotated matrix."
        ),
        input_format="Line 1: JSON 2D array matrix",
        output_format="JSON 2D array rotated matrix",
        constraints="n == matrix.length == matrix[i].length\n1 <= n <= 20\n-1000 <= matrix[i][j] <= 1000",
        method_name="rotate",
        parameters=[{"name": "matrix", "type": "int[][]"}],
        return_type="int[][]",
        samples=[
            _dump_case([[[1, 2, 3], [4, 5, 6], [7, 8, 9]]], [[7, 4, 1], [8, 5, 2], [9, 6, 3]]),
            _dump_case(
                [[[5, 1, 9, 11], [2, 4, 8, 10], [13, 3, 6, 7], [15, 14, 12, 16]]],
                [[15, 13, 2, 5], [14, 3, 4, 1], [12, 6, 8, 9], [16, 7, 10, 11]],
            ),
        ],
        tests=[
            _dump_case([[[1]]], [[1]]),
            _dump_case([[[1, 2], [3, 4]]], [[3, 1], [4, 2]]),
        ],
        generator_count=50,
        generator_seed=21024,
        generator=_gen_module(
            '''
def solve(matrix: list[list[int]]) -> list[list[int]]:
    n = len(matrix)
    for i in range(n):
        for j in range(i + 1, n):
            matrix[i][j], matrix[j][i] = matrix[j][i], matrix[i][j]
    for row in matrix:
        row.reverse()
    return matrix
''',
            '''
def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    for offset in range(count):
        n = rng.randint(1, 8)
        matrix = [[rng.randint(-20, 20) for _ in range(n)] for _ in range(n)]
        m2 = [row[:] for row in matrix]
        yield {
            "input": json.dumps(matrix),
            "expected_output": json.dumps(solve(m2)),
            "order_index": start_index + offset,
            "is_sample": False,
        }
''',
        ),
        # Driver calls method but may not capture in-place mutation for non-returning — we return matrix
        mutate_return=True,
    )

    # NOTE: rotate typically returns void in LC. Our driver expects a return value.
    # We document return of rotated matrix; solution should return the matrix after rotating.

    # 25 Spiral Matrix
    add(
        slug="spiral-matrix",
        title="Spiral Matrix",
        difficulty="medium",
        rating=1100,
        topic="Matrix",
        companies=_companies(*FAANG_PLUS, "Oracle"),
        description=(
            "Given an m x n matrix, return all elements of the matrix in spiral order."
        ),
        input_format="Line 1: JSON 2D array matrix",
        output_format="JSON array of elements in spiral order",
        constraints="m == matrix.length\nn == matrix[i].length\n1 <= m, n <= 10\n-100 <= matrix[i][j] <= 100",
        method_name="spiralOrder",
        parameters=[{"name": "matrix", "type": "int[][]"}],
        return_type="int[]",
        samples=[
            _dump_case([[[1, 2, 3], [4, 5, 6], [7, 8, 9]]], [1, 2, 3, 6, 9, 8, 7, 4, 5]),
            _dump_case([[[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]]], [1, 2, 3, 4, 8, 12, 11, 10, 9, 5, 6, 7]),
        ],
        tests=[
            _dump_case([[[1]]], [1]),
            _dump_case([[[1, 2], [3, 4]]], [1, 2, 4, 3]),
            _dump_case([[[1, 2, 3]]], [1, 2, 3]),
            _dump_case([[[1], [2], [3]]], [1, 2, 3]),
        ],
        generator_count=60,
        generator_seed=21025,
        generator=_gen_module(
            '''
def solve(matrix: list[list[int]]) -> list[int]:
    res = []
    while matrix:
        res += matrix.pop(0)
        if matrix and matrix[0]:
            for row in matrix:
                res.append(row.pop())
        if matrix:
            res += matrix.pop()[::-1]
        if matrix and matrix[0]:
            for row in matrix[::-1]:
                res.append(row.pop(0))
    return res
''',
            '''
def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    for offset in range(count):
        m, n = rng.randint(1, 6), rng.randint(1, 6)
        matrix = [[rng.randint(-20, 20) for _ in range(n)] for _ in range(m)]
        yield {
            "input": json.dumps(matrix),
            "expected_output": json.dumps(solve([row[:] for row in matrix])),
            "order_index": start_index + offset,
            "is_sample": False,
        }
''',
        ),
    )

    # 26 Number of 1 Bits
    add(
        slug="number-of-1-bits",
        title="Number of 1 Bits",
        difficulty="easy",
        rating=800,
        topic="Bit Manipulation",
        companies=_companies(*FAANG_PLUS, "Apple"),
        description=(
            "Write a function that takes an unsigned integer and returns the number of '1' bits it has "
            "(also known as the Hamming weight)."
        ),
        input_format="Line 1: integer n",
        output_format="Integer hamming weight",
        constraints="0 <= n <= 2^31 - 1",
        method_name="hammingWeight",
        parameters=[{"name": "n", "type": "int"}],
        return_type="int",
        samples=[
            _dump_case([11], 3),
            _dump_case([128], 1),
            _dump_case([2147483645], 30),
        ],
        tests=[
            _dump_case([0], 0),
            _dump_case([1], 1),
            _dump_case([255], 8),
        ],
        generator_count=80,
        generator_seed=21026,
        generator=_gen_module(
            '''
def solve(n: int) -> int:
    return n.bit_count()
''',
            '''
def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    for offset in range(count):
        n = rng.randint(0, 2**31 - 1)
        yield {
            "input": json.dumps(n),
            "expected_output": json.dumps(solve(n)),
            "order_index": start_index + offset,
            "is_sample": False,
        }
''',
        ),
    )

    # 27 Counting Bits
    add(
        slug="counting-bits",
        title="Counting Bits",
        difficulty="easy",
        rating=900,
        topic="Bit Manipulation",
        companies=_companies(*FAANG_PLUS),
        description=(
            "Given an integer n, return an array ans of length n + 1 such that for each i (0 <= i <= n), "
            "ans[i] is the number of 1's in the binary representation of i."
        ),
        input_format="Line 1: integer n",
        output_format="JSON array ans",
        constraints="0 <= n <= 10^5",
        method_name="countBits",
        parameters=[{"name": "n", "type": "int"}],
        return_type="int[]",
        samples=[
            _dump_case([2], [0, 1, 1]),
            _dump_case([5], [0, 1, 1, 2, 1, 2]),
        ],
        tests=[
            _dump_case([0], [0]),
            _dump_case([1], [0, 1]),
            _dump_case([8], [0, 1, 1, 2, 1, 2, 2, 3, 1]),
        ],
        generator_count=40,
        generator_seed=21027,
        generator=_gen_module(
            '''
def solve(n: int) -> list[int]:
    ans = [0] * (n + 1)
    for i in range(1, n + 1):
        ans[i] = ans[i >> 1] + (i & 1)
    return ans
''',
            '''
def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    for offset in range(count):
        n = rng.randint(0, 200)
        yield {
            "input": json.dumps(n),
            "expected_output": json.dumps(solve(n)),
            "order_index": start_index + offset,
            "is_sample": False,
        }
''',
        ),
    )

    # 28 Reverse Bits
    add(
        slug="reverse-bits",
        title="Reverse Bits",
        difficulty="easy",
        rating=900,
        topic="Bit Manipulation",
        companies=_companies(*APPLE_AMZN, "Meta", "Microsoft"),
        description=(
            "Reverse bits of a given 32 bits unsigned integer.\n"
            "Note: treat n as an unsigned 32-bit value."
        ),
        input_format="Line 1: integer n",
        output_format="Integer with reversed bits",
        constraints="The input is a 32-bit unsigned integer.",
        method_name="reverseBits",
        parameters=[{"name": "n", "type": "int"}],
        return_type="int",
        samples=[
            _dump_case([43261596], 964176192),
            _dump_case([4294967293], 3221225471),
        ],
        tests=[
            _dump_case([0], 0),
            _dump_case([1], 2147483648),
            _dump_case([2147483648], 1),
        ],
        generator_count=60,
        generator_seed=21028,
        generator=_gen_module(
            '''
def solve(n: int) -> int:
    res = 0
    for _ in range(32):
        res = (res << 1) | (n & 1)
        n >>= 1
    return res
''',
            '''
def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    for offset in range(count):
        n = rng.randint(0, 2**32 - 1)
        yield {
            "input": json.dumps(n),
            "expected_output": json.dumps(solve(n)),
            "order_index": start_index + offset,
            "is_sample": False,
        }
''',
        ),
    )

    # 29 Sum of Two Integers
    add(
        slug="sum-of-two-integers",
        title="Sum of Two Integers",
        difficulty="medium",
        rating=1200,
        topic="Bit Manipulation",
        companies=_companies(*APPLE_AMZN, "Microsoft", "Google"),
        description=(
            "Given two integers a and b, return the sum of the two integers without using the operators + and -."
        ),
        input_format="Line 1: integer a\nLine 2: integer b",
        output_format="Integer sum",
        constraints="-1000 <= a, b <= 1000",
        method_name="getSum",
        parameters=[{"name": "a", "type": "int"}, {"name": "b", "type": "int"}],
        return_type="int",
        samples=[
            _dump_case([1, 2], 3),
            _dump_case([2, 3], 5),
        ],
        tests=[
            _dump_case([0, 0], 0),
            _dump_case([-1, 1], 0),
            _dump_case([-2, -3], -5),
            _dump_case([1000, -1000], 0),
        ],
        generator_count=100,
        generator_seed=21029,
        generator=_gen_module(
            '''
def solve(a: int, b: int) -> int:
    # Python ints are unbounded; mask to 32-bit two's complement behavior
    MASK = 0xFFFFFFFF
    MAX = 0x7FFFFFFF
    while b & MASK:
        carry = (a & b) << 1
        a = (a ^ b) & MASK
        b = carry & MASK
    return a if a <= MAX else ~(a ^ MASK)
''',
            '''
def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    for offset in range(count):
        a, b = rng.randint(-1000, 1000), rng.randint(-1000, 1000)
        yield {
            "input": f"{json.dumps(a)}\\n{json.dumps(b)}",
            "expected_output": json.dumps(solve(a, b)),
            "order_index": start_index + offset,
            "is_sample": False,
        }
''',
        ),
    )

    # 30 Happy Number
    add(
        slug="happy-number",
        title="Happy Number",
        difficulty="easy",
        rating=900,
        topic="Hash Map",
        companies=_companies("Uber", "Google", "Amazon", "Apple", "Adobe"),
        description=(
            "Write an algorithm to determine if a number n is happy.\n"
            "A happy number is a number defined by the following process: Starting with any positive integer, "
            "replace the number by the sum of the squares of its digits. Repeat until the number equals 1 "
            "(where it will stay), or it loops endlessly in a cycle which does not include 1. "
            "Those numbers for which this process ends in 1 are happy.\n"
            "Return true if n is a happy number, and false if not."
        ),
        input_format="Line 1: integer n",
        output_format="Boolean true/false",
        constraints="1 <= n <= 2^31 - 1",
        method_name="isHappy",
        parameters=[{"name": "n", "type": "int"}],
        return_type="bool",
        samples=[
            _dump_case([19], True),
            _dump_case([2], False),
        ],
        tests=[
            _dump_case([1], True),
            _dump_case([7], True),
            _dump_case([4], False),
        ],
        generator_count=80,
        generator_seed=21030,
        generator=_gen_module(
            '''
def solve(n: int) -> bool:
    seen = set()
    while n != 1 and n not in seen:
        seen.add(n)
        n = sum(int(d) ** 2 for d in str(n))
    return n == 1
''',
            '''
def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    for offset in range(count):
        n = rng.randint(1, 500)
        yield {
            "input": json.dumps(n),
            "expected_output": json.dumps(solve(n)),
            "order_index": start_index + offset,
            "is_sample": False,
        }
''',
        ),
    )

    # 31 Subarray Sum Equals K
    add(
        slug="subarray-sum-equals-k",
        title="Subarray Sum Equals K",
        difficulty="medium",
        rating=1200,
        topic="Hash Map",
        companies=_companies(*GOOG_META, "Amazon", "Uber", "LinkedIn"),
        description=(
            "Given an array of integers nums and an integer k, return the total number of subarrays whose sum equals k.\n"
            "A subarray is a contiguous non-empty sequence of elements within an array."
        ),
        input_format="Line 1: JSON array nums\nLine 2: integer k",
        output_format="Integer count",
        constraints="1 <= nums.length <= 2*10^4\n-1000 <= nums[i] <= 1000\n-10^7 <= k <= 10^7",
        method_name="subarraySum",
        parameters=[{"name": "nums", "type": "int[]"}, {"name": "k", "type": "int"}],
        return_type="int",
        samples=[
            _dump_case([[1, 1, 1], 2], 2),
            _dump_case([[1, 2, 3], 3], 2),
        ],
        tests=[
            _dump_case([[1], 0], 0),
            _dump_case([[1], 1], 1),
            _dump_case([[-1, -1, 1], 0], 1),
            _dump_case([[0, 0, 0], 0], 6),
        ],
        generator_count=80,
        generator_seed=21031,
        generator=_gen_module(
            '''
def solve(nums: list[int], k: int) -> int:
    prefix = 0
    cnt = defaultdict(int)
    cnt[0] = 1
    ans = 0
    for x in nums:
        prefix += x
        ans += cnt[prefix - k]
        cnt[prefix] += 1
    return ans
''',
            '''
def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    for offset in range(count):
        n = rng.randint(1, 40)
        nums = [rng.randint(-10, 10) for _ in range(n)]
        k = rng.randint(-20, 20)
        yield {
            "input": f"{json.dumps(nums)}\\n{json.dumps(k)}",
            "expected_output": json.dumps(solve(nums, k)),
            "order_index": start_index + offset,
            "is_sample": False,
        }
''',
        ),
    )

    # 32 4Sum
    add(
        slug="4sum",
        title="4Sum",
        difficulty="medium",
        rating=1200,
        topic="Two Pointers",
        companies=_companies(*AMZN_GOOG, "Meta", "Adobe"),
        description=(
            "Given an array nums of n integers, return an array of all the unique quadruplets "
            "[nums[a], nums[b], nums[c], nums[d]] such that 0 <= a, b, c, d < n, a/b/c/d are distinct, "
            "and nums[a] + nums[b] + nums[c] + nums[d] == target.\n"
            "You may return the answer in any order."
        ),
        input_format="Line 1: JSON array nums\nLine 2: integer target",
        output_format="JSON 2D array of unique quadruplets",
        constraints="1 <= nums.length <= 200\n-10^9 <= nums[i] <= 10^9\n-10^9 <= target <= 10^9",
        method_name="fourSum",
        parameters=[{"name": "nums", "type": "int[]"}, {"name": "target", "type": "int"}],
        return_type="int[][]",
        samples=[
            _dump_case([[1, 0, -1, 0, -2, 2], 0], [[-2, -1, 1, 2], [-2, 0, 0, 2], [-1, 0, 0, 1]]),
            _dump_case([[2, 2, 2, 2, 2], 8], [[2, 2, 2, 2]]),
        ],
        tests=[
            _dump_case([[1, 2], 3], []),
            _dump_case([[0, 0, 0, 0], 0], [[0, 0, 0, 0]]),
        ],
        generator_count=50,
        generator_seed=21032,
        generator=_gen_module(
            '''
def solve(nums: list[int], target: int) -> list[list[int]]:
    nums.sort()
    n = len(nums)
    res = []
    for i in range(n):
        if i and nums[i] == nums[i - 1]:
            continue
        for j in range(i + 1, n):
            if j > i + 1 and nums[j] == nums[j - 1]:
                continue
            l, r = j + 1, n - 1
            while l < r:
                s = nums[i] + nums[j] + nums[l] + nums[r]
                if s == target:
                    res.append([nums[i], nums[j], nums[l], nums[r]])
                    l += 1
                    r -= 1
                    while l < r and nums[l] == nums[l - 1]:
                        l += 1
                    while l < r and nums[r] == nums[r + 1]:
                        r -= 1
                elif s < target:
                    l += 1
                else:
                    r -= 1
    return res
''',
            '''
def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    for offset in range(count):
        n = rng.randint(4, 12)
        nums = [rng.randint(-20, 20) for _ in range(n)]
        target = rng.randint(-40, 40)
        yield {
            "input": f"{json.dumps(nums)}\\n{json.dumps(target)}",
            "expected_output": json.dumps(solve(nums[:], target)),
            "order_index": start_index + offset,
            "is_sample": False,
        }
''',
        ),
        sort_output=True,
    )

    # 33 Single Number
    add(
        slug="single-number",
        title="Single Number",
        difficulty="easy",
        rating=850,
        topic="Bit Manipulation",
        companies=_companies(*FAANG_PLUS),
        description=(
            "Given a non-empty array of integers nums, every element appears twice except for one. "
            "Find that single one.\nYou must implement a solution with a linear runtime complexity and use only constant extra space."
        ),
        input_format="Line 1: JSON array nums",
        output_format="Integer single number",
        constraints="1 <= nums.length <= 3*10^4\n-3*10^4 <= nums[i] <= 3*10^4\nEach element appears twice except one.",
        method_name="singleNumber",
        parameters=[{"name": "nums", "type": "int[]"}],
        return_type="int",
        samples=[
            _dump_case([[2, 2, 1]], 1),
            _dump_case([[4, 1, 2, 1, 2]], 4),
            _dump_case([[1]], 1),
        ],
        tests=[
            _dump_case([[0, 1, 0]], 1),
            _dump_case([[-1, -1, 2]], 2),
        ],
        generator_count=80,
        generator_seed=21033,
        generator=_gen_module(
            '''
def solve(nums: list[int]) -> int:
    x = 0
    for v in nums:
        x ^= v
    return x
''',
            '''
def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    for offset in range(count):
        k = rng.randint(0, 15)
        pairs = rng.sample(range(-50, 51), k + 1)
        single = pairs[0]
        nums = []
        for p in pairs[1:]:
            nums.extend([p, p])
        nums.append(single)
        rng.shuffle(nums)
        yield {
            "input": json.dumps(nums),
            "expected_output": json.dumps(solve(nums)),
            "order_index": start_index + offset,
            "is_sample": False,
        }
''',
        ),
    )

    # 34 Valid Sudoku
    add(
        slug="valid-sudoku",
        title="Valid Sudoku",
        difficulty="medium",
        rating=1100,
        topic="Hash Map",
        companies=_companies(*FAANG_PLUS, "Apple"),
        description=(
            "Determine if a 9 x 9 Sudoku board is valid. Only the filled cells need to be validated according "
            "to the following rules: each row, each column, and each of the nine 3x3 sub-boxes must contain "
            "the digits 1-9 without repetition.\n"
            "Note: A Sudoku board (partially filled) could be valid but is not necessarily solvable. "
            "Board is given as string[] of length 9 (each string length 9, '.' for empty)."
        ),
        input_format="Line 1: JSON array of 9 strings (rows)",
        output_format="Boolean true/false",
        constraints="board.length == 9\nboard[i].length == 9\nboard[i][j] is a digit 1-9 or '.'",
        method_name="isValidSudoku",
        parameters=[{"name": "board", "type": "str[]"}],
        return_type="bool",
        samples=[
            _dump_case([
                [
                    "53..7....",
                    "6..195...",
                    ".98....6.",
                    "8...6...3",
                    "4..8.3..1",
                    "7...2...6",
                    ".6....28.",
                    "...419..5",
                    "....8..79",
                ]
            ], True),
            _dump_case([
                [
                    "83..7....",
                    "6..195...",
                    ".98....6.",
                    "8...6...3",
                    "4..8.3..1",
                    "7...2...6",
                    ".6....28.",
                    "...419..5",
                    "....8..79",
                ]
            ], False),
        ],
        tests=[
            _dump_case([["." * 9] * 9], True),
            _dump_case([["1" + "." * 8, "." * 9, "." * 9, "." * 9, "." * 9, "." * 9, "." * 9, "." * 9, "1" + "." * 8]], True),
            _dump_case([["1" + "." * 8, "." * 9, "." * 9, "." * 9, "." * 9, "." * 9, "." * 9, "." * 9, "1......."]], False),  # same col? wait row0 col0 and row8 col0 both 1 - invalid
        ],
        generator_count=40,
        generator_seed=21034,
        generator=_gen_module(
            '''
def solve(board: list[str]) -> bool:
    rows = [set() for _ in range(9)]
    cols = [set() for _ in range(9)]
    boxes = [set() for _ in range(9)]
    for i in range(9):
        for j in range(9):
            ch = board[i][j]
            if ch == ".":
                continue
            b = (i // 3) * 3 + j // 3
            if ch in rows[i] or ch in cols[j] or ch in boxes[b]:
                return False
            rows[i].add(ch)
            cols[j].add(ch)
            boxes[b].add(ch)
    return True
''',
            '''
def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    for offset in range(count):
        board = [["."] * 9 for _ in range(9)]
        # place a few digits without conflict when possible
        for _ in range(rng.randint(0, 15)):
            i, j = rng.randint(0, 8), rng.randint(0, 8)
            d = str(rng.randint(1, 9))
            board[i][j] = d
        # occasionally force conflict
        if rng.random() < 0.3:
            board[0][0] = board[0][1] = "5"
        rows = ["".join(r) for r in board]
        yield {
            "input": json.dumps(rows),
            "expected_output": json.dumps(solve(rows)),
            "order_index": start_index + offset,
            "is_sample": False,
        }
''',
        ),
    )

    # Fix valid sudoku edge: two 1s in same column
    P[-1]["tests"][-1] = _dump_case(
        [["1........", ".........", ".........", ".........", ".........", ".........", ".........", ".........", "1........"]],
        False,
    )

    # 35 Find All Anagrams
    add(
        slug="find-all-anagrams-in-a-string",
        title="Find All Anagrams in a String",
        difficulty="medium",
        rating=1150,
        topic="Sliding Window",
        companies=_companies(*AMZN_META, "Google", "Uber"),
        description=(
            "Given two strings s and p, return an array of all the start indices of p's anagrams in s. "
            "You may return the answer in any order."
        ),
        input_format="Line 1: string s\nLine 2: string p",
        output_format="JSON array of start indices",
        constraints="1 <= s.length, p.length <= 3*10^4\ns and p consist of lowercase English letters.",
        method_name="findAnagrams",
        parameters=[{"name": "s", "type": "str"}, {"name": "p", "type": "str"}],
        return_type="int[]",
        samples=[
            _dump_case(["cbaebabacd", "abc"], [0, 6]),
            _dump_case(["abab", "ab"], [0, 1, 2]),
        ],
        tests=[
            _dump_case(["a", "a"], [0]),
            _dump_case(["a", "b"], []),
            _dump_case(["baa", "aa"], [1]),
        ],
        generator_count=60,
        generator_seed=21035,
        generator=_gen_module(
            '''
def solve(s: str, p: str) -> list[int]:
    if len(p) > len(s):
        return []
    need = Counter(p)
    window = Counter()
    res = []
    for i, ch in enumerate(s):
        window[ch] += 1
        if i >= len(p):
            left = s[i - len(p)]
            window[left] -= 1
            if window[left] == 0:
                del window[left]
        if i >= len(p) - 1 and window == need:
            res.append(i - len(p) + 1)
    return res
''',
            '''
def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    letters = "abcde"
    for offset in range(count):
        s = "".join(rng.choice(letters) for _ in range(rng.randint(1, 40)))
        p = "".join(rng.choice(letters) for _ in range(rng.randint(1, 5)))
        yield {
            "input": f"{json.dumps(s)}\\n{json.dumps(p)}",
            "expected_output": json.dumps(solve(s, p)),
            "order_index": start_index + offset,
            "is_sample": False,
        }
''',
        ),
        sort_output=True,
    )

    # 36 Is Subsequence
    add(
        slug="is-subsequence",
        title="Is Subsequence",
        difficulty="easy",
        rating=850,
        topic="Two Pointers",
        companies=_companies("Google", "Amazon", "Meta", "Pinterest", "Uber"),  # Pinterest filtered
        description=(
            "Given two strings s and t, return true if s is a subsequence of t, or false otherwise.\n"
            "A subsequence of a string is a new string that is formed from the original string by deleting some "
            "(can be none) of the characters without disturbing the relative positions of the remaining characters."
        ),
        input_format="Line 1: string s\nLine 2: string t",
        output_format="Boolean true/false",
        constraints="0 <= s.length <= 100\n0 <= t.length <= 10^4\ns and t consist only of lowercase English letters.",
        method_name="isSubsequence",
        parameters=[{"name": "s", "type": "str"}, {"name": "t", "type": "str"}],
        return_type="bool",
        samples=[
            _dump_case(["abc", "ahbgdc"], True),
            _dump_case(["axc", "ahbgdc"], False),
        ],
        tests=[
            _dump_case(["", "ahbgdc"], True),
            _dump_case(["abc", ""], False),
            _dump_case(["b", "abc"], True),
        ],
        generator_count=80,
        generator_seed=21036,
        generator=_gen_module(
            '''
def solve(s: str, t: str) -> bool:
    i = 0
    for ch in t:
        if i < len(s) and s[i] == ch:
            i += 1
    return i == len(s)
''',
            '''
def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    letters = "abcd"
    for offset in range(count):
        t = "".join(rng.choice(letters) for _ in range(rng.randint(0, 30)))
        if rng.random() < 0.5 and t:
            s = "".join(t[i] for i in sorted(rng.sample(range(len(t)), rng.randint(0, len(t)))))
        else:
            s = "".join(rng.choice(letters) for _ in range(rng.randint(0, 8)))
        yield {
            "input": f"{json.dumps(s)}\\n{json.dumps(t)}",
            "expected_output": json.dumps(solve(s, t)),
            "order_index": start_index + offset,
            "is_sample": False,
        }
''',
        ),
    )

    # 37 Reverse Words in a String
    add(
        slug="reverse-words-in-a-string",
        title="Reverse Words in a String",
        difficulty="medium",
        rating=1000,
        topic="String",
        companies=_companies(*AMZN_META, "Microsoft", "Apple", "Uber"),
        description=(
            "Given an input string s, reverse the order of the words.\n"
            "A word is defined as a sequence of non-space characters. The words in s will be separated by at least one space.\n"
            "Return a string of the words in reverse order concatenated by a single space.\n"
            "Note that s may contain leading or trailing spaces or multiple spaces between two words. "
            "The returned string should only have a single space separating the words. Do not include any extra spaces."
        ),
        input_format="Line 1: string s",
        output_format="String with words reversed",
        constraints="1 <= s.length <= 10^4\ns contains English letters, digits, and spaces",
        method_name="reverseWords",
        parameters=[{"name": "s", "type": "str"}],
        return_type="str",
        samples=[
            _dump_case(["the sky is blue"], "blue is sky the"),
            _dump_case(["  hello world  "], "world hello"),
            _dump_case(["a good   example"], "example good a"),
        ],
        tests=[
            _dump_case(["word"], "word"),
            _dump_case(["   a   b  "], "b a"),
        ],
        generator_count=60,
        generator_seed=21037,
        generator=_gen_module(
            '''
def solve(s: str) -> str:
    return " ".join(reversed(s.split()))
''',
            '''
def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    words_pool = ["the", "sky", "is", "blue", "hello", "world", "a", "good", "example", "code"]
    for offset in range(count):
        words = [rng.choice(words_pool) for _ in range(rng.randint(1, 8))]
        gaps = [" " * rng.randint(1, 3) for _ in range(len(words) - 1)]
        s = (" " * rng.randint(0, 2))
        for i, w in enumerate(words):
            s += w
            if i < len(gaps):
                s += gaps[i]
        s += " " * rng.randint(0, 2)
        yield {
            "input": json.dumps(s),
            "expected_output": json.dumps(solve(s)),
            "order_index": start_index + offset,
            "is_sample": False,
        }
''',
        ),
    )

    # Continue with trees, graphs, more DP — part2b inline
    return extend_more_b(P)


def extend_more_b(P: list[dict]) -> list[dict]:
    def add(**kwargs):
        companies = kwargs.pop("companies")
        kwargs["companies"] = [c for c in companies if c in HUB_NAMES]
        P.append(kwargs)

    # 38 LCA of BST
    add(
        slug="lowest-common-ancestor-of-a-binary-search-tree",
        title="Lowest Common Ancestor of a Binary Search Tree",
        difficulty="medium",
        rating=1050,
        topic="Trees",
        companies=_companies(*FAANG_PLUS),
        description=(
            "Given a binary search tree (BST), find the lowest common ancestor (LCA) node of two given nodes "
            "in the BST.\nAccording to the definition of LCA on Wikipedia: “The lowest common ancestor is defined "
            "between two nodes p and q as the lowest node in T that has both p and q as descendants "
            "(where we allow a node to be a descendant of itself).”\n"
            "Inputs: root as level-order array; p and q as integer values present in the tree. Return the LCA node value "
            "as a single-node TreeNode array."
        ),
        input_format="Line 1: JSON array root\nLine 2: integer p\nLine 3: integer q",
        output_format="JSON level-order array for LCA TreeNode",
        constraints="The number of nodes in the tree is in the range [2, 10^5].\nAll Node.val are unique.\np != q\np and q will exist in the BST.",
        method_name="lowestCommonAncestor",
        parameters=[
            {"name": "root", "type": "TreeNode"},
            {"name": "p", "type": "TreeNode"},
            {"name": "q", "type": "TreeNode"},
        ],
        return_type="TreeNode",
        samples=[
            # p and q as TreeNode arrays with single value
            ("[6,2,8,0,4,7,9,null,null,3,5]\n[2]\n[8]", "[6]"),
            ("[6,2,8,0,4,7,9,null,null,3,5]\n[2]\n[4]", "[2]"),
        ],
        tests=[
            ("[2,1]\n[2]\n[1]", "[2]"),
            ("[5,3,6,2,4,null,null,1]\n[1]\n[4]", "[3]"),
        ],
        generator_count=50,
        generator_seed=21038,
        generator=_gen_module(
            '''
def solve(root, p, q):
    # p,q are TreeNode; compare values
    pv, qv = p.val, q.val
    node = root
    while node:
        if pv < node.val and qv < node.val:
            node = node.left
        elif pv > node.val and qv > node.val:
            node = node.right
        else:
            return node
    return None
''',
            '''
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
        vals = rng.sample(range(1, 40), rng.randint(3, 12))
        root = None
        for v in vals:
            root = _insert(root, v)
        pval, qval = rng.sample(vals, 2)
        # Walk solve
        node = root
        while node:
            if pval < node.val and qval < node.val:
                node = node.left
            elif pval > node.val and qval > node.val:
                node = node.right
            else:
                break
        yield {
            "input": f"{json.dumps(tree_to_list(root))}\\n{json.dumps([pval])}\\n{json.dumps([qval])}",
            "expected_output": json.dumps(tree_to_list(node)),
            "order_index": start_index + offset,
            "is_sample": False,
        }
''',
            tree=True,
        ),
    )

    # 39 Subtree of Another Tree
    add(
        slug="subtree-of-another-tree",
        title="Subtree of Another Tree",
        difficulty="easy",
        rating=1000,
        topic="Trees",
        companies=_companies(*AMZN_META, "Google", "Microsoft"),
        description=(
            "Given the roots of two binary trees root and subRoot, return true if there is a subtree of root "
            "with the same structure and node values of subRoot and false otherwise.\n"
            "A subtree of a binary tree tree is a tree that consists of a node in tree and all of this node's descendants."
        ),
        input_format="Line 1: JSON array root\nLine 2: JSON array subRoot",
        output_format="Boolean true/false",
        constraints="The number of nodes in the root tree is in the range [1, 2000].\nThe number of nodes in the subRoot tree is in the range [1, 1000].",
        method_name="isSubtree",
        parameters=[{"name": "root", "type": "TreeNode"}, {"name": "subRoot", "type": "TreeNode"}],
        return_type="bool",
        samples=[
            ("[3,4,5,1,2]\n[4,1,2]", "true"),
            ("[3,4,5,1,2,null,null,null,null,0]\n[4,1,2]", "false"),
        ],
        tests=[
            ("[1]\n[1]", "true"),
            ("[1,1]\n[1]", "true"),
            ("[1,2,3]\n[4]", "false"),
        ],
        generator_count=50,
        generator_seed=21039,
        generator=_gen_module(
            '''
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
''',
            '''
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
            "input": f"{json.dumps(root_list)}\\n{json.dumps(sub)}",
            "expected_output": json.dumps(solve(root, subRoot)),
            "order_index": start_index + offset,
            "is_sample": False,
        }
''',
            tree=True,
        ),
    )

    # 40 Count Good Nodes
    add(
        slug="count-good-nodes-in-binary-tree",
        title="Count Good Nodes in Binary Tree",
        difficulty="medium",
        rating=1100,
        topic="Trees",
        companies=_companies(*AMZN_META, "Microsoft", "Apple"),
        description=(
            "Given a binary tree root, a node X in the tree is named good if in the path from root to X there are "
            "no nodes with a value greater than X.\nReturn the number of good nodes in the binary tree."
        ),
        input_format="Line 1: JSON array root",
        output_format="Integer count of good nodes",
        constraints="The number of nodes in the binary tree is in the range [1, 10^5].\nEach node's value is between [-10^4, 10^4].",
        method_name="goodNodes",
        parameters=[{"name": "root", "type": "TreeNode"}],
        return_type="int",
        samples=[
            ("[3,1,4,3,null,1,5]", "4"),
            ("[3,3,null,4,2]", "3"),
            ("[1]", "1"),
        ],
        tests=[
            ("[2,null,4,10,8,null,null,4]", "4"),
            ("[0,null,-1]", "1"),
        ],
        generator_count=60,
        generator_seed=21040,
        generator=_gen_module(
            '''
def solve(root) -> int:
    def dfs(node, mx):
        if not node:
            return 0
        good = 1 if node.val >= mx else 0
        nmx = max(mx, node.val)
        return good + dfs(node.left, nmx) + dfs(node.right, nmx)
    return dfs(root, float("-inf"))
''',
            '''
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
''',
            tree=True,
        ),
    )

    # 41 Binary Tree Inorder Traversal
    add(
        slug="binary-tree-inorder-traversal",
        title="Binary Tree Inorder Traversal",
        difficulty="easy",
        rating=850,
        topic="Trees",
        companies=_companies(*FAANG_PLUS),
        description="Given the root of a binary tree, return the inorder traversal of its nodes' values.",
        input_format="Line 1: JSON array root",
        output_format="JSON array of values in inorder",
        constraints="The number of nodes in the tree is in the range [0, 100].\n-100 <= Node.val <= 100",
        method_name="inorderTraversal",
        parameters=[{"name": "root", "type": "TreeNode"}],
        return_type="int[]",
        samples=[
            ("[1,null,2,3]", "[1,3,2]"),
            ("[]", "[]"),
            ("[1]", "[1]"),
        ],
        tests=[
            ("[1,2]", "[2,1]"),
            ("[1,null,2]", "[1,2]"),
        ],
        generator_count=60,
        generator_seed=21041,
        generator=_gen_module(
            '''
def solve(root) -> list[int]:
    res = []
    def dfs(node):
        if not node:
            return
        dfs(node.left)
        res.append(node.val)
        dfs(node.right)
    dfs(root)
    return res
''',
            '''
def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    for offset in range(count):
        if rng.random() < 0.1:
            vals = []
        else:
            vals = [rng.randint(-20, 20) for _ in range(rng.randint(1, 12))]
        root = build_tree(vals)
        yield {
            "input": json.dumps(vals if vals else []),
            "expected_output": json.dumps(solve(root)),
            "order_index": start_index + offset,
            "is_sample": False,
        }
''',
            tree=True,
        ),
    )

    # 42 Range Sum of BST
    add(
        slug="range-sum-of-bst",
        title="Range Sum of BST",
        difficulty="easy",
        rating=900,
        topic="Trees",
        companies=_companies(*AMZN_META, "Google", "Microsoft"),
        description=(
            "Given the root node of a binary search tree and two integers low and high, return the sum of values "
            "of all nodes with a value in the inclusive range [low, high]."
        ),
        input_format="Line 1: JSON array root\nLine 2: integer low\nLine 3: integer high",
        output_format="Integer range sum",
        constraints="The number of nodes in the tree is in the range [1, 2*10^4].\n1 <= Node.val <= 10^5\n1 <= low <= high <= 10^5\nAll Node.val are unique.",
        method_name="rangeSumBST",
        parameters=[
            {"name": "root", "type": "TreeNode"},
            {"name": "low", "type": "int"},
            {"name": "high", "type": "int"},
        ],
        return_type="int",
        samples=[
            ("[10,5,15,3,7,null,18]\n7\n15", "32"),
            ("[10,5,15,3,7,13,18,1,null,6]\n6\n10", "23"),
        ],
        tests=[
            ("[1]\n1\n1", "1"),
            ("[5,3,8]\n1\n10", "16"),
        ],
        generator_count=60,
        generator_seed=21042,
        generator=_gen_module(
            '''
def solve(root, low: int, high: int) -> int:
    if not root:
        return 0
    if root.val < low:
        return solve(root.right, low, high)
    if root.val > high:
        return solve(root.left, low, high)
    return root.val + solve(root.left, low, high) + solve(root.right, low, high)
''',
            '''
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
            "input": f"{json.dumps(tree_to_list(root))}\\n{json.dumps(low)}\\n{json.dumps(high)}",
            "expected_output": json.dumps(solve(root, low, high)),
            "order_index": start_index + offset,
            "is_sample": False,
        }
''',
            tree=True,
        ),
    )

    # 43 Number of Provinces
    add(
        slug="number-of-provinces",
        title="Number of Provinces",
        difficulty="medium",
        rating=1100,
        topic="Graphs",
        companies=_companies(*AMZN_GOOG, "Meta", "Uber"),
        description=(
            "There are n cities. Some of them are connected, while some are not. If city a is connected directly "
            "with city b, and city b is connected directly with city c, then city a is connected indirectly with city c.\n"
            "A province is a group of directly or indirectly connected cities and no other cities outside of the group.\n"
            "You are given an n x n matrix isConnected where isConnected[i][j] = 1 if the ith city and the jth city "
            "are directly connected, and isConnected[i][j] = 0 otherwise.\nReturn the total number of provinces."
        ),
        input_format="Line 1: JSON 2D array isConnected",
        output_format="Integer number of provinces",
        constraints="1 <= n <= 200\nn == isConnected.length\nn == isConnected[i].length\nisConnected[i][j] is 1 or 0\nisConnected[i][i] == 1\nisConnected[i][j] == isConnected[j][i]",
        method_name="findCircleNum",
        parameters=[{"name": "isConnected", "type": "int[][]"}],
        return_type="int",
        samples=[
            _dump_case([[[1, 1, 0], [1, 1, 0], [0, 0, 1]]], 2),
            _dump_case([[[1, 0, 0], [0, 1, 0], [0, 0, 1]]], 3),
        ],
        tests=[
            _dump_case([[[1]]], 1),
            _dump_case([[[1, 1], [1, 1]]], 1),
        ],
        generator_count=60,
        generator_seed=21043,
        generator=_gen_module(
            '''
def solve(isConnected: list[list[int]]) -> int:
    n = len(isConnected)
    seen = [False] * n
    def dfs(i):
        for j in range(n):
            if isConnected[i][j] and not seen[j]:
                seen[j] = True
                dfs(j)
    provinces = 0
    for i in range(n):
        if not seen[i]:
            seen[i] = True
            dfs(i)
            provinces += 1
    return provinces
''',
            '''
def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    for offset in range(count):
        n = rng.randint(1, 12)
        g = [[0] * n for _ in range(n)]
        for i in range(n):
            g[i][i] = 1
            for j in range(i + 1, n):
                if rng.random() < 0.25:
                    g[i][j] = g[j][i] = 1
        yield {
            "input": json.dumps(g),
            "expected_output": json.dumps(solve(g)),
            "order_index": start_index + offset,
            "is_sample": False,
        }
''',
        ),
    )

    # 44 Max Area of Island
    add(
        slug="max-area-of-island",
        title="Max Area of Island",
        difficulty="medium",
        rating=1100,
        topic="Graphs",
        companies=_companies(*AMZN_META, "Google", "Microsoft"),
        description=(
            "You are given an m x n binary matrix grid. An island is a group of 1's (representing land) connected "
            "4-directionally (horizontal or vertical). You may assume all four edges of the grid are surrounded by water.\n"
            "The area of an island is the number of cells with a value 1 in the island.\n"
            "Return the maximum area of an island in grid. If there is no island, return 0."
        ),
        input_format="Line 1: JSON 2D array grid",
        output_format="Integer max area",
        constraints="m == grid.length\nn == grid[i].length\n1 <= m, n <= 50\ngrid[i][j] is 0 or 1",
        method_name="maxAreaOfIsland",
        parameters=[{"name": "grid", "type": "int[][]"}],
        return_type="int",
        samples=[
            _dump_case([[[0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0], [0, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0], [0, 1, 0, 0, 1, 1, 0, 0, 1, 0, 1, 0, 0], [0, 1, 0, 0, 1, 1, 0, 0, 1, 1, 1, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0], [0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0]]], 6),
            _dump_case([[[0, 0, 0, 0, 0, 0, 0, 0]]], 0),
        ],
        tests=[
            _dump_case([[[1]]], 1),
            _dump_case([[[1, 1], [1, 0]]], 3),
            _dump_case([[[0]]], 0),
        ],
        generator_count=60,
        generator_seed=21044,
        generator=_gen_module(
            '''
def solve(grid: list[list[int]]) -> int:
    m, n = len(grid), len(grid[0])
    def dfs(i, j):
        if i < 0 or j < 0 or i >= m or j >= n or grid[i][j] != 1:
            return 0
        grid[i][j] = 0
        return 1 + dfs(i+1,j) + dfs(i-1,j) + dfs(i,j+1) + dfs(i,j-1)
    best = 0
    for i in range(m):
        for j in range(n):
            if grid[i][j] == 1:
                best = max(best, dfs(i, j))
    return best
''',
            '''
def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    for offset in range(count):
        m, n = rng.randint(1, 10), rng.randint(1, 10)
        grid = [[1 if rng.random() < 0.35 else 0 for _ in range(n)] for _ in range(m)]
        yield {
            "input": json.dumps(grid),
            "expected_output": json.dumps(solve([row[:] for row in grid])),
            "order_index": start_index + offset,
            "is_sample": False,
        }
''',
        ),
    )

    # 45 01 Matrix
    add(
        slug="01-matrix",
        title="01 Matrix",
        difficulty="medium",
        rating=1200,
        topic="Graphs",
        companies=_companies(*GOOG_AMZN, "Meta", "Microsoft"),
        description=(
            "Given an m x n binary matrix mat, return the distance of the nearest 0 for each cell.\n"
            "The distance between two cells sharing a common edge is 1."
        ),
        input_format="Line 1: JSON 2D array mat",
        output_format="JSON 2D array of distances",
        constraints="m == mat.length\nn == mat[i].length\n1 <= m, n <= 50\n1 <= m * n <= 10^4\nmat[i][j] is 0 or 1\nThere is at least one 0 in mat.",
        method_name="updateMatrix",
        parameters=[{"name": "mat", "type": "int[][]"}],
        return_type="int[][]",
        samples=[
            _dump_case([[[0, 0, 0], [0, 1, 0], [0, 0, 0]]], [[0, 0, 0], [0, 1, 0], [0, 0, 0]]),
            _dump_case([[[0, 0, 0], [0, 1, 0], [1, 1, 1]]], [[0, 0, 0], [0, 1, 0], [1, 2, 1]]),
        ],
        tests=[
            _dump_case([[[0]]], [[0]]),
            _dump_case([[[1, 0]]], [[1, 0]]),
            _dump_case([[[1, 1], [1, 0]]], [[2, 1], [1, 0]]),
        ],
        generator_count=50,
        generator_seed=21045,
        generator=_gen_module(
            '''
def solve(mat: list[list[int]]) -> list[list[int]]:
    m, n = len(mat), len(mat[0])
    INF = 10**9
    dist = [[INF] * n for _ in range(m)]
    q = deque()
    for i in range(m):
        for j in range(n):
            if mat[i][j] == 0:
                dist[i][j] = 0
                q.append((i, j))
    while q:
        r, c = q.popleft()
        for nr, nc in ((r+1,c),(r-1,c),(r,c+1),(r,c-1)):
            if 0 <= nr < m and 0 <= nc < n and dist[nr][nc] > dist[r][c] + 1:
                dist[nr][nc] = dist[r][c] + 1
                q.append((nr, nc))
    return dist
''',
            '''
def generate_cases(*, count: int, seed: int, start_index: int):
    rng = random.Random(seed)
    for offset in range(count):
        m, n = rng.randint(1, 8), rng.randint(1, 8)
        mat = [[1 if rng.random() < 0.7 else 0 for _ in range(n)] for _ in range(m)]
        if all(all(x == 1 for x in row) for row in mat):
            mat[0][0] = 0
        yield {
            "input": json.dumps(mat),
            "expected_output": json.dumps(solve([row[:] for row in mat])),
            "order_index": start_index + offset,
            "is_sample": False,
        }
''',
        ),
    )

    from backend.tools.scaffold_batch_dsa_problems_part3 import extend_final
    return extend_final(P)

