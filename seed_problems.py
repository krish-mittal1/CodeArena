#!/usr/bin/env python3
"""
Seed script: inserts 22 competitive programming problems with 40-50 test cases each.
Uses asyncpg (already in the api venv). Run inside the api container:
  docker exec api sh -c 'cd /app && .venv/bin/python /tmp/seed_problems.py'
"""

import asyncio
import uuid
import asyncpg

DB_DSN = "postgresql://postgres:krishisunique@api_postgres:5432/codexarena"

PROBLEMS = [
    # ── 800-rated ─────────────────────────────────────────────────
    {
        "title": "Odd or Even",
        "description": (
            "Given an integer N, print \"Odd\" if N is odd, otherwise print \"Even\".\n\n"
            "**Example:**\n"
            "Input: 4  →  Output: Even\n"
            "Input: 7  →  Output: Odd"
        ),
        "difficulty": "easy",
        "rating": 800,
        "input_format": "A single integer N.",
        "output_format": "Print \"Odd\" or \"Even\" (without quotes).",
        "constraints": "1 ≤ N ≤ 10^9",
        "time_limit_ms": 1000,
        "memory_limit_mb": 256,
        "gen": lambda: [(str(i), "Even" if i % 2 == 0 else "Odd") for i in
                        [1, 2, 3, 4, 0, -1, -2, 100, 999, 1000,
                         1_000_000_000, 999_999_999, 2, 7, 13, 100, 101,
                         8, 15, 22, 33, 44, 55, 66, 77, 88, 99,
                         1_000_000, 1_000_001, 50, 51, 52, 53, 54, 55,
                         200, 201, 300, 400, 500, 501, 777, 888, 999, 10]],
    },
    {
        "title": "Sum of Digits",
        "description": (
            "Given a positive integer N, find the sum of its digits.\n\n"
            "**Example:**\n"
            "Input: 123  →  Output: 6\n"
            "Input: 999  →  Output: 27"
        ),
        "difficulty": "easy",
        "rating": 800,
        "input_format": "A single positive integer N.",
        "output_format": "Print the sum of digits of N.",
        "constraints": "1 ≤ N ≤ 10^9",
        "time_limit_ms": 1000,
        "memory_limit_mb": 256,
        "gen": lambda: [(str(n), str(sum(int(d) for d in str(n)))) for n in
                        [1, 9, 10, 99, 100, 123, 999, 1234, 9999, 10000,
                         100000, 999999, 1000000, 123456789, 1000000000,
                         111111111, 222222222, 333333333, 555, 777,
                         2, 3, 4, 5, 19, 29, 39, 49, 59, 69,
                         100000000, 200000000, 999999999, 987654321,
                         11, 22, 33, 44, 55, 66, 88, 121, 1001, 10001]],
    },
    {
        "title": "Maximum of Three",
        "description": (
            "Given three integers A, B, C on a single line, print the largest among them.\n\n"
            "**Example:**\n"
            "Input: 3 1 2  →  Output: 3"
        ),
        "difficulty": "easy",
        "rating": 800,
        "input_format": "Three integers A B C on a single line.",
        "output_format": "Print the maximum value.",
        "constraints": "-10^9 ≤ A, B, C ≤ 10^9",
        "time_limit_ms": 1000,
        "memory_limit_mb": 256,
        "gen": lambda: [(" ".join(map(str, t)), str(max(t))) for t in
                        [(1,2,3),(3,2,1),(2,3,1),(1,1,1),(-1,-2,-3),
                         (0,0,0),(1000000000,-1000000000,0),
                         (-5,-5,-5),(100,100,99),(1,1,2),
                         (3,3,3),(7,3,5),(8,8,9),(0,1,0),(0,0,1),
                         (-1,0,1),(999,998,997),(1,999,500),
                         (1000000000,999999999,999999998),
                         (-1000000000,-999999999,-999999998),
                         (5,5,4),(4,5,5),(5,4,5),(100,200,300),
                         (300,200,100),(200,300,100),(1,2,2),(2,1,2),(2,2,1),
                         (0,-1,-2),(-2,-1,0),(1000,1000,1000),
                         (10,20,15),(50,50,25),(0,0,-1),
                         (999999999,1000000000,0),(2,2,3),(3,3,2),(1,3,2),
                         (9,8,7),(7,9,8),(8,7,9),(3,1,4),(4,1,3),(1,4,3)]],
    },
    # ── 900-rated ─────────────────────────────────────────────────
    {
        "title": "Reverse a String",
        "description": (
            "Given a string S, print the reverse of S.\n\n"
            "**Example:**\n"
            "Input: hello  →  Output: olleh"
        ),
        "difficulty": "easy",
        "rating": 900,
        "input_format": "A single string S with no spaces.",
        "output_format": "Print the reversed string.",
        "constraints": "1 ≤ |S| ≤ 10^5, S contains only lowercase English letters.",
        "time_limit_ms": 1000,
        "memory_limit_mb": 256,
        "gen": lambda: [(s, s[::-1]) for s in
                        ["a","z","ab","ba","abc","cba","hello","world",
                         "abcde","edcba","racecar","level","noon","civic",
                         "aabbcc","xyzxyz","abcdefg","aaaa","bbbb","cccc",
                         "abcba","abccba","python","coding","arena",
                         "competitive","algorithm","datastructure",
                         "a"*100,"b"*99+"a","z"*50+"a"*50,
                         "abcdefghij","jihgfedcba","qwerty","ytrewq",
                         "mnop","ponm","xyz","zyx","ab"*10,"ba"*10,
                         "az","za","bz","zb","mn","nm","yz","zy","cd","dc"]],
    },
    {
        "title": "Count Vowels",
        "description": (
            "Given a string S, count the number of vowels (a, e, i, o, u) in it.\n\n"
            "**Example:**\n"
            "Input: hello  →  Output: 2"
        ),
        "difficulty": "easy",
        "rating": 900,
        "input_format": "A single string S (lowercase letters only).",
        "output_format": "Print the count of vowels.",
        "constraints": "1 ≤ |S| ≤ 10^5",
        "time_limit_ms": 1000,
        "memory_limit_mb": 256,
        "gen": lambda: [(s, str(sum(1 for c in s if c in "aeiou"))) for s in
                        ["a","b","hello","world","aeiou","bcdfg","programming",
                         "competitive","coding","arena","aaaa","bbbb",
                         "aeioubcdfg","bcdfgaeiou","university","algorithm",
                         "z","xy","qu","ieee","queue","euouae",
                         "rhythms","tryst","strength","crypt",
                         "education","beautiful","sequoia","facetious",
                         "a"*100,"b"*100,"aeiou"*20,"bcdfg"*20,
                         "abcde","fghij","klmno","pqrst","uvwxy",
                         "aabbccddee","aabbcc","iioouuee","aaeeiioouu",
                         "hello world".replace(" ",""),"python","java"]],
    },
    {
        "title": "Binary to Decimal",
        "description": (
            "Given a binary string S (containing only 0s and 1s), convert it to its decimal equivalent.\n\n"
            "**Example:**\n"
            "Input: 1010  →  Output: 10"
        ),
        "difficulty": "easy",
        "rating": 900,
        "input_format": "A binary string S.",
        "output_format": "Print the decimal equivalent.",
        "constraints": "1 ≤ |S| ≤ 30",
        "time_limit_ms": 1000,
        "memory_limit_mb": 256,
        "gen": lambda: [(s, str(int(s, 2))) for s in
                        ["0","1","10","11","100","101","110","111","1000",
                         "1010","1111","10000","10101","11111","100000",
                         "101010","111111","1000000","1010101","1111111",
                         "10000000","101010101","111111111","1000000000",
                         "1073741823","1111111111","10111011010",
                         "0","1","01","001","0001","11110000","00001111",
                         "10101010","01010101","11001100","00110011",
                         "11111111","100000000","111111110","11111111111",
                         "111111111111111","11111111111111","1111111111111",
                         "111111111111","10000000000","11000000000"]],
    },
    # ── 1000-rated ────────────────────────────────────────────────
    {
        "title": "Two Sum",
        "description": (
            "Given an array of N integers and a target T, find two distinct indices i and j "
            "such that arr[i] + arr[j] = T. Print the 0-based indices in ascending order.\n"
            "It is guaranteed that exactly one solution exists.\n\n"
            "**Example:**\n"
            "Input:\n4 9\n2 7 11 15\n"
            "Output: 0 1"
        ),
        "difficulty": "easy",
        "rating": 1000,
        "input_format": "Line 1: N and T. Line 2: N space-separated integers.",
        "output_format": "Two 0-based indices i j (i < j) such that arr[i]+arr[j]=T.",
        "constraints": "2 ≤ N ≤ 10^4, -10^9 ≤ arr[i], T ≤ 10^9",
        "time_limit_ms": 2000,
        "memory_limit_mb": 256,
        "gen": lambda: _two_sum_cases(),
    },
    {
        "title": "Fibonacci Number",
        "description": (
            "Given N, print the N-th Fibonacci number (0-indexed: F(0)=0, F(1)=1).\n\n"
            "**Example:**\n"
            "Input: 6  →  Output: 8"
        ),
        "difficulty": "easy",
        "rating": 1000,
        "input_format": "A single integer N.",
        "output_format": "Print the N-th Fibonacci number.",
        "constraints": "0 ≤ N ≤ 50",
        "time_limit_ms": 1000,
        "memory_limit_mb": 256,
        "gen": lambda: _fib_cases(),
    },
    {
        "title": "Check Palindrome",
        "description": (
            "Given a string S, determine if it is a palindrome. Print \"YES\" if it is, \"NO\" otherwise.\n\n"
            "**Example:**\n"
            "Input: racecar  →  Output: YES\n"
            "Input: hello  →  Output: NO"
        ),
        "difficulty": "easy",
        "rating": 1000,
        "input_format": "A single string S (lowercase letters only, no spaces).",
        "output_format": "Print YES or NO.",
        "constraints": "1 ≤ |S| ≤ 10^5",
        "time_limit_ms": 1000,
        "memory_limit_mb": 256,
        "gen": lambda: [(s, "YES" if s == s[::-1] else "NO") for s in
                        ["a","aa","ab","aba","abc","abba","abcba","level",
                         "racecar","hello","world","noon","civic","kayak",
                         "deified","aabbaa","abcabc","aaaa","aaab","abcd",
                         "abcba","abccba","abcbca","abcdcba","abcddcba",
                         "a"*100,"a"*99+"b","b"+"a"*99,
                         "amanaplanacanalpanama","wasitacaroracatisaw",
                         "neverodoroven","abba","abbc","deed","dood",
                         "madam","radar","refer","rotor","redder",
                         "repaper","reviver","rotator","sagas","sexes",
                         "solos","stats","stets","sumus","tenet","umamu"]],
    },
    # ── 1100-rated ────────────────────────────────────────────────
    {
        "title": "Prefix Sum Query",
        "description": (
            "Given an array of N integers, answer Q queries. Each query gives l and r (1-based), "
            "and you must print the sum of elements from index l to r (inclusive).\n\n"
            "**Example:**\n"
            "Input:\n5 3\n1 2 3 4 5\n1 3\n2 4\n1 5\n"
            "Output:\n6\n9\n15"
        ),
        "difficulty": "medium",
        "rating": 1100,
        "input_format": "Line 1: N Q. Line 2: N integers. Next Q lines: l r.",
        "output_format": "Print Q lines, each with the sum for that query.",
        "constraints": "1 ≤ N, Q ≤ 10^5, -10^9 ≤ arr[i] ≤ 10^9, 1 ≤ l ≤ r ≤ N",
        "time_limit_ms": 2000,
        "memory_limit_mb": 256,
        "gen": lambda: _prefix_sum_cases(),
    },
    {
        "title": "GCD of Array",
        "description": (
            "Given an array of N positive integers, find the GCD of all elements.\n\n"
            "**Example:**\n"
            "Input:\n4\n12 8 6 4\n"
            "Output: 2"
        ),
        "difficulty": "medium",
        "rating": 1100,
        "input_format": "Line 1: N. Line 2: N space-separated integers.",
        "output_format": "Print the GCD of all elements.",
        "constraints": "1 ≤ N ≤ 10^5, 1 ≤ arr[i] ≤ 10^9",
        "time_limit_ms": 2000,
        "memory_limit_mb": 256,
        "gen": lambda: _gcd_cases(),
    },
    {
        "title": "Count Pairs with Given Sum",
        "description": (
            "Given an array of N integers and a target K, count the number of pairs (i, j) "
            "with i < j such that arr[i] + arr[j] = K.\n\n"
            "**Example:**\n"
            "Input:\n5 6\n1 5 7 1 5\n"
            "Output: 3"
        ),
        "difficulty": "medium",
        "rating": 1100,
        "input_format": "Line 1: N and K. Line 2: N space-separated integers.",
        "output_format": "Print the count of such pairs.",
        "constraints": "1 ≤ N ≤ 10^4, -10^9 ≤ arr[i], K ≤ 10^9",
        "time_limit_ms": 2000,
        "memory_limit_mb": 256,
        "gen": lambda: _count_pairs_cases(),
    },
    # ── 1200-rated ────────────────────────────────────────────────
    {
        "title": "Longest Increasing Subsequence Length",
        "description": (
            "Given an array of N integers, find the length of the Longest Strictly Increasing Subsequence (LIS).\n\n"
            "**Example:**\n"
            "Input:\n6\n10 9 2 5 3 7\n"
            "Output: 3"
        ),
        "difficulty": "medium",
        "rating": 1200,
        "input_format": "Line 1: N. Line 2: N space-separated integers.",
        "output_format": "Print the length of the LIS.",
        "constraints": "1 ≤ N ≤ 2500, -10^9 ≤ arr[i] ≤ 10^9",
        "time_limit_ms": 3000,
        "memory_limit_mb": 256,
        "gen": lambda: _lis_cases(),
    },
    {
        "title": "Number of Islands",
        "description": (
            "Given an N×M grid of '0's (water) and '1's (land), count the number of islands. "
            "An island is a maximal group of '1' cells connected horizontally or vertically.\n\n"
            "**Example:**\n"
            "Input:\n3 4\n1100\n1100\n0011\n"
            "Output: 2"
        ),
        "difficulty": "medium",
        "rating": 1200,
        "input_format": "Line 1: N M. Next N lines: a string of '0'/'1' of length M.",
        "output_format": "Print the number of islands.",
        "constraints": "1 ≤ N, M ≤ 300",
        "time_limit_ms": 3000,
        "memory_limit_mb": 256,
        "gen": lambda: _island_cases(),
    },
    {
        "title": "Maximum Subarray Sum (Kadane)",
        "description": (
            "Given an array of N integers, find the maximum sum of any contiguous subarray.\n\n"
            "**Example:**\n"
            "Input:\n8\n-2 1 -3 4 -1 2 1 -5 4\n"
            "Output: 6"
        ),
        "difficulty": "medium",
        "rating": 1200,
        "input_format": "Line 1: N. Line 2: N space-separated integers.",
        "output_format": "Print the maximum subarray sum.",
        "constraints": "1 ≤ N ≤ 10^5, -10^9 ≤ arr[i] ≤ 10^9",
        "time_limit_ms": 2000,
        "memory_limit_mb": 256,
        "gen": lambda: _kadane_cases(),
    },
    {
        "title": "Binary Search",
        "description": (
            "Given a sorted array of N distinct integers and a target T, print the 0-based index of T. "
            "If T is not in the array, print -1.\n\n"
            "**Example:**\n"
            "Input:\n5 7\n1 3 5 7 9\n"
            "Output: 3"
        ),
        "difficulty": "easy",
        "rating": 1000,
        "input_format": "Line 1: N and T. Line 2: N sorted distinct integers.",
        "output_format": "Print the 0-based index of T, or -1.",
        "constraints": "1 ≤ N ≤ 10^6, -10^9 ≤ arr[i], T ≤ 10^9",
        "time_limit_ms": 2000,
        "memory_limit_mb": 256,
        "gen": lambda: _binary_search_cases(),
    },
    {
        "title": "Stack: Valid Parentheses",
        "description": (
            "Given a string S containing only '(', ')', '{', '}', '[' and ']', determine if the brackets are valid.\n"
            "A valid string has every open bracket closed by the same type in correct order.\n"
            "Print \"YES\" if valid, \"NO\" otherwise.\n\n"
            "**Example:**\n"
            "Input: ()[]{}  →  Output: YES\n"
            "Input: (]  →  Output: NO"
        ),
        "difficulty": "medium",
        "rating": 1100,
        "input_format": "A single string S.",
        "output_format": "Print YES or NO.",
        "constraints": "1 ≤ |S| ≤ 10^4",
        "time_limit_ms": 1000,
        "memory_limit_mb": 256,
        "gen": lambda: _parens_cases(),
    },
    {
        "title": "Prime Factorization",
        "description": (
            "Given a positive integer N > 1, print its prime factors in ascending order, each on its own line, "
            "with repetition.\n\n"
            "**Example:**\n"
            "Input: 12  →  Output:\n2\n2\n3"
        ),
        "difficulty": "easy",
        "rating": 900,
        "input_format": "A single integer N.",
        "output_format": "Print prime factors in ascending order, one per line.",
        "constraints": "2 ≤ N ≤ 10^7",
        "time_limit_ms": 2000,
        "memory_limit_mb": 256,
        "gen": lambda: _prime_factor_cases(),
    },
    {
        "title": "Merge Sorted Arrays",
        "description": (
            "Given two sorted arrays A (of size N) and B (of size M), merge them into a single sorted array "
            "and print all elements.\n\n"
            "**Example:**\n"
            "Input:\n3\n1 3 5\n4\n2 4 6 8\n"
            "Output: 1 2 3 4 5 6 8"
        ),
        "difficulty": "easy",
        "rating": 1000,
        "input_format": "Line 1: N. Line 2: N sorted integers. Line 3: M. Line 4: M sorted integers.",
        "output_format": "Print the merged sorted array space-separated.",
        "constraints": "0 ≤ N, M ≤ 10^5, -10^9 ≤ arr[i] ≤ 10^9",
        "time_limit_ms": 2000,
        "memory_limit_mb": 256,
        "gen": lambda: _merge_cases(),
    },
    {
        "title": "Minimum Jumps to Reach End",
        "description": (
            "Given an array of N non-negative integers where arr[i] represents the max jump length from index i, "
            "find the minimum number of jumps to reach the last index from index 0. If impossible, print -1.\n\n"
            "**Example:**\n"
            "Input:\n6\n2 3 1 1 4 0\n"
            "Output: 2"
        ),
        "difficulty": "medium",
        "rating": 1200,
        "input_format": "Line 1: N. Line 2: N space-separated integers.",
        "output_format": "Print minimum jumps or -1 if impossible.",
        "constraints": "1 ≤ N ≤ 10^4, 0 ≤ arr[i] ≤ 10^4",
        "time_limit_ms": 2000,
        "memory_limit_mb": 256,
        "gen": lambda: _jump_cases(),
    },
    {
        "title": "Anagram Check",
        "description": (
            "Given two strings A and B of the same length, determine if B is an anagram of A. "
            "Print \"YES\" if they are anagrams, \"NO\" otherwise.\n\n"
            "**Example:**\n"
            "Input:\nlisten\nsilent\n"
            "Output: YES"
        ),
        "difficulty": "easy",
        "rating": 900,
        "input_format": "Two strings A and B on separate lines.",
        "output_format": "Print YES or NO.",
        "constraints": "1 ≤ |A| = |B| ≤ 10^5, only lowercase letters.",
        "time_limit_ms": 1000,
        "memory_limit_mb": 256,
        "gen": lambda: _anagram_cases(),
    },
    {
        "title": "Shortest Path in Grid (BFS)",
        "description": (
            "Given an N×M grid where '.' is open and '#' is blocked, find the shortest path "
            "from top-left (0,0) to bottom-right (N-1,M-1) in number of steps. "
            "Movement: up, down, left, right. Print -1 if unreachable.\n\n"
            "**Example:**\n"
            "Input:\n3 3\n...\n.#.\n...\n"
            "Output: 4"
        ),
        "difficulty": "medium",
        "rating": 1200,
        "input_format": "Line 1: N M. Next N lines: M characters ('.' or '#').",
        "output_format": "Print shortest path length or -1.",
        "constraints": "1 ≤ N, M ≤ 500",
        "time_limit_ms": 3000,
        "memory_limit_mb": 256,
        "gen": lambda: _bfs_grid_cases(),
    },
    {
        "title": "Majority Element",
        "description": (
            "Given an array of N integers, find the element that appears more than N/2 times. "
            "It is guaranteed such an element exists.\n\n"
            "**Example:**\n"
            "Input:\n7\n2 2 1 1 1 2 2\n"
            "Output: 2"
        ),
        "difficulty": "medium",
        "rating": 1100,
        "input_format": "Line 1: N. Line 2: N space-separated integers.",
        "output_format": "Print the majority element.",
        "constraints": "1 ≤ N ≤ 10^5, -10^9 ≤ arr[i] ≤ 10^9, N is odd.",
        "time_limit_ms": 2000,
        "memory_limit_mb": 256,
        "gen": lambda: _majority_cases(),
    },
    {
        "title": "Rotate Array",
        "description": (
            "Given an array of N integers and a value K, rotate the array to the right by K positions.\n\n"
            "**Example:**\n"
            "Input:\n5 2\n1 2 3 4 5\n"
            "Output: 4 5 1 2 3"
        ),
        "difficulty": "easy",
        "rating": 800,
        "input_format": "Line 1: N and K. Line 2: N space-separated integers.",
        "output_format": "Print the rotated array space-separated.",
        "constraints": "1 ≤ N ≤ 10^5, 0 ≤ K ≤ 10^9",
        "time_limit_ms": 1000,
        "memory_limit_mb": 256,
        "gen": lambda: _rotate_cases(),
    },
]

# ── Helper generators ─────────────────────────────────────────────

def _two_sum_cases():
    import random; random.seed(42)
    cases = []
    tests = [
        ([2,7,11,15],9),([3,2,4],6),([3,3],6),
        ([1,2,3,4,5],9),([0,4,3,0],0),([-1,-2,-3,-4,-5],-8),
        ([1000000000,-1000000000,0,1],1),([-5,10,5,3,8],15),
        ([1,2],3),([100,200,300],500),
    ]
    for arr,t in tests:
        for i in range(len(arr)):
            for j in range(i+1,len(arr)):
                if arr[i]+arr[j]==t:
                    inp = f"{len(arr)} {t}\n{' '.join(map(str,arr))}"
                    cases.append((inp, f"{i} {j}")); break
            else: continue
            break
    # random cases
    for _ in range(35):
        n = random.randint(2,20)
        arr = [random.randint(-100,100) for _ in range(n)]
        i,j = random.sample(range(n),2)
        if i>j: i,j=j,i
        t = arr[i]+arr[j]
        inp = f"{n} {t}\n{' '.join(map(str,arr))}"
        cases.append((inp, f"{i} {j}"))
    return cases[:45]

def _fib_cases():
    fibs=[0,1]
    for _ in range(49): fibs.append(fibs[-1]+fibs[-2])
    return [(str(i),str(fibs[i])) for i in range(51)][:45]

def _prefix_sum_cases():
    import random; random.seed(7)
    cases=[]
    arrs=[
        ([1,2,3,4,5],[(1,3),(2,4),(1,5),(3,5),(1,1),(5,5)]),
        ([-1,-2,-3,-4,-5],[(1,5),(1,3),(3,5),(2,4),(1,2),(4,5)]),
        ([1000000000]*5,[(1,5),(1,1),(5,5),(2,4),(1,4),(3,5)]),
    ]
    for arr,qs in arrs:
        n=len(arr); ps=[0]*(n+1)
        for i in range(n): ps[i+1]=ps[i]+arr[i]
        for l,r in qs:
            inp=f"{n} 1\n{' '.join(map(str,arr))}\n{l} {r}"
            cases.append((inp,str(ps[r]-ps[l-1])))
    for _ in range(35):
        n=random.randint(1,10); arr=[random.randint(-1000,1000) for _ in range(n)]
        ps=[0]*(n+1)
        for i in range(n): ps[i+1]=ps[i]+arr[i]
        l=random.randint(1,n); r=random.randint(l,n)
        inp=f"{n} 1\n{' '.join(map(str,arr))}\n{l} {r}"
        cases.append((inp,str(ps[r]-ps[l-1])))
    return cases[:45]

def _gcd_cases():
    import math, random; random.seed(3)
    cases=[]
    tests=[[12,8,6,4],[7,14,21],[100],[17],[1000000000,500000000],
           [1,1,1,1],[2,3,5,7],[6,10,15],[999999999,333333333],
           [12,18,24,36,48]]
    for arr in tests:
        g=arr[0]
        for x in arr[1:]: g=math.gcd(g,x)
        cases.append((f"{len(arr)}\n{' '.join(map(str,arr))}",str(g)))
    for _ in range(35):
        base=random.choice([1,2,3,5,7,11,13])
        n=random.randint(1,8)
        arr=[base*random.randint(1,100) for _ in range(n)]
        g=arr[0]
        for x in arr[1:]: g=math.gcd(g,x)
        cases.append((f"{n}\n{' '.join(map(str,arr))}",str(g)))
    return cases[:45]

def _count_pairs_cases():
    import random; random.seed(11)
    def count(arr,k): return sum(1 for i in range(len(arr)) for j in range(i+1,len(arr)) if arr[i]+arr[j]==k)
    cases=[]
    tests=[([1,5,7,1,5],6),([1,1,1,1],2),([0,0,0],0),([1,2,3],6),([-1,-1,2],1),([5],5)]
    for arr,k in tests:
        cases.append((f"{len(arr)} {k}\n{' '.join(map(str,arr))}",str(count(arr,k))))
    for _ in range(39):
        n=random.randint(2,15); arr=[random.randint(-20,20) for _ in range(n)]
        k=random.randint(-30,30)
        cases.append((f"{n} {k}\n{' '.join(map(str,arr))}",str(count(arr,k))))
    return cases[:45]

def _lis_cases():
    def lis(a):
        import bisect; tails=[]
        for x in a:
            pos=bisect.bisect_left(tails,x)
            if pos==len(tails): tails.append(x)
            else: tails[pos]=x
        return len(tails)
    import random; random.seed(99)
    cases=[]
    tests=[[10,9,2,5,3,7],[0,1,0,3,2,3],[7,7,7,7],[1],[1,2],
           [5,4,3,2,1],[1,2,3,4,5],[3,1,4,1,5,9,2,6],
           [10,9,2,5,3,4],[1,3,2,4,3,5]]
    for arr in tests:
        cases.append((f"{len(arr)}\n{' '.join(map(str,arr))}",str(lis(arr))))
    for _ in range(35):
        n=random.randint(1,20); arr=[random.randint(-50,50) for _ in range(n)]
        cases.append((f"{n}\n{' '.join(map(str,arr))}",str(lis(arr))))
    return cases[:45]

def _island_cases():
    def count_islands(grid):
        n,m=len(grid),len(grid[0]); visited=[[False]*m for _ in range(n)]; cnt=0
        def dfs(i,j):
            if i<0 or i>=n or j<0 or j>=m or visited[i][j] or grid[i][j]=='0': return
            visited[i][j]=True
            for di,dj in[(-1,0),(1,0),(0,-1),(0,1)]: dfs(i+di,j+dj)
        for i in range(n):
            for j in range(m):
                if not visited[i][j] and grid[i][j]=='1': dfs(i,j); cnt+=1
        return cnt
    grids=[
        (["1100","1100","0011"],2),(["1111","1111"],1),(["0000"],0),
        (["1010","0101","1010"],5),(["1"],1),(["0"],0),
        (["11","11"],1),(["10","01"],2),(["111","010","111"],1),
        (["1000","0100","0010","0001"],4),
    ]
    import random; random.seed(55)
    cases=[]
    for grid,_ in grids:
        ans=count_islands(grid)
        inp=f"{len(grid)} {len(grid[0])}\n"+"\n".join(grid)
        cases.append((inp,str(ans)))
    for _ in range(35):
        n=random.randint(1,8); m=random.randint(1,8)
        grid=["".join(random.choice("01") for _ in range(m)) for _ in range(n)]
        ans=count_islands(grid)
        inp=f"{n} {m}\n"+"\n".join(grid)
        cases.append((inp,str(ans)))
    return cases[:45]

def _kadane_cases():
    def kadane(a):
        ms=cs=a[0]
        for x in a[1:]: cs=max(x,cs+x); ms=max(ms,cs)
        return ms
    import random; random.seed(17)
    cases=[]
    tests=[[-2,1,-3,4,-1,2,1,-5,4],[1],[-1],[-2,-3,-4,-5],
           [1,2,3,4,5],[100,-1,100],[0,0,0],[1000000000,-1,1000000000],
           [-1000000000,1,-1000000000],[-1,-2,-3,-4,-5]]
    for arr in tests:
        cases.append((f"{len(arr)}\n{' '.join(map(str,arr))}",str(kadane(arr))))
    for _ in range(35):
        n=random.randint(1,20); arr=[random.randint(-100,100) for _ in range(n)]
        cases.append((f"{n}\n{' '.join(map(str,arr))}",str(kadane(arr))))
    return cases[:45]

def _binary_search_cases():
    import random; random.seed(8)
    cases=[]
    tests=[([1,3,5,7,9],7),([1,3,5,7,9],6),([1],1),([1],2),
           ([-5,-3,-1,0,2,4],0),([-5,-3,-1,0,2,4],-3),
           ([1000000000],1000000000),([1000000000],999999999),
           ([1,2],1),([1,2],2),([1,2],3)]
    for arr,t in tests:
        try: idx=arr.index(t)
        except ValueError: idx=-1
        cases.append((f"{len(arr)} {t}\n{' '.join(map(str,arr))}",str(idx)))
    for _ in range(34):
        n=random.randint(1,20); arr=sorted(random.sample(range(-200,200),min(n,400)))
        n=len(arr)
        t=random.randint(-200,200)
        try: idx=arr.index(t)
        except ValueError: idx=-1
        cases.append((f"{n} {t}\n{' '.join(map(str,arr))}",str(idx)))
    return cases[:45]

def _parens_cases():
    def ok(s):
        st=[]; m={')':'(',']':'[','}':'{'}
        for c in s:
            if c in '([{': st.append(c)
            else:
                if not st or st[-1]!=m[c]: return "NO"
                st.pop()
        return "YES" if not st else "NO"
    tests=["()","[]","{}","()[]{}","(]","([)]","{[]}","","(",")",
           "((()))","((())","((()))","(((",")))","([{}])","[({})","{}()[]",
           "(()","()()","{}{}","[][]","({})","[()]","(([]{}))","([]{})",
           ")(","}{","]['","][","({[","]})","{([])}","({}[])",
           "((((((",")))))))","(){}[]","({}","{})","{()}","[{}]","[{()}]"]
    return [(s,ok(s)) for s in tests if s][:45]

def _prime_factor_cases():
    def pf(n):
        fs=[]; d=2
        while d*d<=n:
            while n%d==0: fs.append(d); n//=d
            d+=1
        if n>1: fs.append(n)
        return "\n".join(map(str,fs))
    tests=[2,3,4,5,6,7,8,9,10,12,15,16,17,18,20,24,30,36,60,
           100,1000,9999991,9999973,1000003,7919,10000019,
           2*3*5*7*11,2**10,3**8,2*3*5*7,4,6,8,9,10,77,91,
           2*2*3*3*5*5,7*11*13,17*19*23,2*2*2*2*2,3*3*3*3]
    return [(str(n),pf(n)) for n in tests][:45]

def _merge_cases():
    import random; random.seed(22)
    cases=[]
    tests=[([1,3,5],[2,4,6,8]),([],  [1,2,3]),([1,2,3],[]),
           ([1],[1]),([5,10,15],[1,2,3]),([1,1,1],[1,1,1]),
           ([-5,-3,-1],[-2,0,2]),
           ([-1000000000],[1000000000]),([1,2,3,4,5],[6,7,8,9,10])]
    for a,b in tests:
        merged=sorted(a+b); n,m=len(a),len(b)
        inp=f"{n}\n{' '.join(map(str,a))}\n{m}\n{' '.join(map(str,b))}"
        cases.append((inp," ".join(map(str,merged))))
    for _ in range(36):
        n=random.randint(0,10); m=random.randint(0,10)
        a=sorted(random.randint(-100,100) for _ in range(n))
        b=sorted(random.randint(-100,100) for _ in range(m))
        merged=sorted(a+b)
        inp=f"{n}\n{' '.join(map(str,a))}\n{m}\n{' '.join(map(str,b))}"
        cases.append((inp," ".join(map(str,merged))))
    return cases[:45]

def _jump_cases():
    def jump(arr):
        n=len(arr)
        if n==1: return 0
        jumps=curr_end=farthest=0
        for i in range(n-1):
            farthest=max(farthest,i+arr[i])
            if i==curr_end:
                if curr_end<n-1 and farthest==i: return -1
                jumps+=1; curr_end=farthest
                if curr_end>=n-1: break
        return jumps
    import random; random.seed(33)
    cases=[]
    tests=[[2,3,1,1,4,0],[3,2,1,0,4],[0],[1],[2,3,0,1,4],
           [1,1,1,1],[0,0,0,0],[1],[5,4,3,2,1,0],
           [1,0],[2,0],[1,2,3],[3,0,0,0],[0,1]]
    for arr in tests:
        cases.append((f"{len(arr)}\n{' '.join(map(str,arr))}",str(jump(arr))))
    for _ in range(31):
        n=random.randint(1,15); arr=[random.randint(0,5) for _ in range(n)]
        cases.append((f"{n}\n{' '.join(map(str,arr))}",str(jump(arr))))
    return cases[:45]

def _anagram_cases():
    from collections import Counter
    import random, string; random.seed(44)
    def ana(a,b): return "YES" if Counter(a)==Counter(b) else "NO"
    pairs=[("listen","silent"),("hello","world"),("anagram","nagaram"),
           ("rat","car"),("a","a"),("ab","ba"),("abc","abc"),
           ("aabb","bbaa"),("abc","bcd"),("aeiou","oueai"),
           ("listen","tinsel"),("dirty","study"),("moon","mono"),
           ("evil","vile"),("elvis","lives"),("night","thing"),
           ("dusty","study"),("dormitory","dirtyroom"),
           ("schoolmaster","theclassroom"),("astronomer","moonstarer")]
    cases=[(a,b,ana(a,b)) for a,b in pairs]
    for _ in range(25):
        n=random.randint(1,10); a="".join(random.choices(string.ascii_lowercase,k=n))
        b=list(a); random.shuffle(b); b="".join(b)
        if random.random()<0.3: b=b[:-1]+"z"
        if len(b)==len(a): cases.append((a,b,ana(a,b)))
    return [(f"{a}\n{b}",ans) for a,b,ans in cases[:45]]

def _bfs_grid_cases():
    from collections import deque
    def bfs(grid):
        n,m=len(grid),len(grid[0])
        if grid[0][0]=='#' or grid[n-1][m-1]=='#': return -1
        if n==1 and m==1: return 0
        dist=[[-1]*m for _ in range(n)]; dist[0][0]=0; q=deque([(0,0)])
        while q:
            i,j=q.popleft()
            for di,dj in[(-1,0),(1,0),(0,-1),(0,1)]:
                ni,nj=i+di,j+dj
                if 0<=ni<n and 0<=nj<m and dist[ni][nj]==-1 and grid[ni][nj]=='.':
                    dist[ni][nj]=dist[i][j]+1; q.append((ni,nj))
        return dist[n-1][m-1]
    import random; random.seed(66)
    grids=[
        (["...","...","..."],4),(["...","###","..."],-1),
        (["."],0),(["##","#."],-1),(["..",".."],2),
        ([".","."],1),(["..#","...","..."],4),
        (["...","...","..#"],-1),(["...","...",".."],3),
        ([".#",".."],2),
    ]
    cases=[]
    for grid,_ in grids:
        ans=bfs(grid); n,m=len(grid),len(grid[0])
        inp=f"{n} {m}\n"+"\n".join(grid); cases.append((inp,str(ans)))
    for _ in range(35):
        n=random.randint(1,8); m=random.randint(1,8)
        grid=["".join(random.choice(".#.") for _ in range(m)) for _ in range(n)]
        grid[0]='.'+grid[0][1:]; grid[n-1]=grid[n-1][:-1]+'.'
        ans=bfs(grid); inp=f"{n} {m}\n"+"\n".join(grid)
        cases.append((inp,str(ans)))
    return cases[:45]

def _majority_cases():
    import random; random.seed(77)
    def maj(a): m=a[0];c=1;[(m:=x,c:=1) if c==0 else ((c:=c+1) if x==m else (c:=c-1)) for x in a[1:]];return m
    cases=[]
    tests=[[2,2,1,1,1,2,2],[3,3,4,2,4,4,2,4,4],[1],[3,3,3],
           [1,1,2,1,3,1,4],[2,2,2,2,1],[1,2,1,2,1],[5,5,5,5,5],
           [-1,-1,1],[1000000000,1000000000,-1],[-5,-5,-5,-5,1]]
    for arr in tests:
        cases.append((f"{len(arr)}\n{' '.join(map(str,arr))}",str(maj(arr))))
    for _ in range(34):
        n=random.randint(1,19,); n=n if n%2==1 else n+1
        v=random.randint(-100,100); cnt=(n//2)+1
        rest=[random.randint(-100,100) for _ in range(n-cnt)]; arr=[v]*cnt+rest
        random.shuffle(arr); cases.append((f"{len(arr)}\n{' '.join(map(str,arr))}",str(maj(arr))))
    return cases[:45]

def _rotate_cases():
    import random; random.seed(88)
    def rot(arr,k): n=len(arr);k%=n;return arr[n-k:]+arr[:n-k] if n else arr
    cases=[]
    tests=[([1,2,3,4,5],2),([1,2,3,4,5],0),([1,2,3,4,5],5),
           ([1],0),([1,2],1),([1,2,3],6),([3,99,-2,4,7],3),
           ([1,2,3,4,5],1000000000),([5,4,3,2,1],3)]
    for arr,k in tests:
        r=rot(arr,k); inp=f"{len(arr)} {k}\n{' '.join(map(str,arr))}"
        cases.append((inp," ".join(map(str,r))))
    for _ in range(36):
        n=random.randint(1,15); arr=[random.randint(-100,100) for _ in range(n)]
        k=random.randint(0,100); r=rot(arr,k)
        inp=f"{n} {k}\n{' '.join(map(str,arr))}"; cases.append((inp," ".join(map(str,r))))
    return cases[:45]

# ── Main ──────────────────────────────────────────────────────────

async def main():
    conn = await asyncpg.connect(DB_DSN)

    total_problems = 0
    total_cases = 0

    for prob in PROBLEMS:
        prob_id = str(uuid.uuid4())
        await conn.execute(
            """INSERT INTO problems
               (id, title, description, difficulty, input_format, output_format,
                constraints, time_limit_ms, memory_limit_mb, is_active, created_at, rating)
               VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,true,NOW(),$10)
               ON CONFLICT DO NOTHING""",
            uuid.UUID(prob_id), prob["title"], prob["description"], prob["difficulty"],
            prob["input_format"], prob["output_format"], prob["constraints"],
            prob["time_limit_ms"], prob["memory_limit_mb"], prob["rating"]
        )
        cases = prob["gen"]()
        for idx, (inp, out) in enumerate(cases, 1):
            await conn.execute(
                """INSERT INTO test_cases (id, problem_id, input, expected_output, is_sample, order_index)
                   VALUES ($1,$2,$3,$4,$5,$6)""",
                uuid.UUID(str(uuid.uuid4())), uuid.UUID(prob_id), inp, out, idx <= 3, idx
            )
            total_cases += 1
        total_problems += 1
        print(f"  ✔ [{prob['rating']}] {prob['title']} — {len(cases)} test cases")

    await conn.close()
    print(f"\n✅ Done! Inserted {total_problems} problems and {total_cases} test cases.")

if __name__ == "__main__":
    asyncio.run(main())
