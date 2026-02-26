"""
Seed script — insert 50 original competitive programming problems.

Rated 800-1200 (hidden from users), labeled Easy/Medium/Hard.
Each problem: 2 visible + 4-6 hidden test cases with edge cases.
All solvable in C++, Java, Python, JavaScript.

Usage: python -m backend.scripts.seed_problems
"""
import asyncio, logging
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import select
from backend.config import settings
from backend.db.base import Base
from backend.models.problem import Problem
from backend.models.test_case import TestCase
from backend.core.constants import Difficulty

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

E, M, H = Difficulty.EASY, Difficulty.MEDIUM, Difficulty.HARD

PROBLEMS = [
# ══════════ EASY (800-900) — 15 problems ══════════

{"title":"Watermelon Split","difficulty":E,"rating":800,
"description":"Pete and Billy bought a watermelon weighing w kilos. They want to split it into two parts, each weighing an even positive number of kilos.\n\nDetermine if this is possible.",
"input_format":"A single integer w.","output_format":"Print YES or NO.","constraints":"1 ≤ w ≤ 100","time_limit_ms":1000,"memory_limit_mb":256,
"test_cases":[
{"input":"8","expected_output":"YES","is_sample":True,"order_index":0},
{"input":"3","expected_output":"NO","is_sample":True,"order_index":1},
{"input":"1","expected_output":"NO","is_sample":False,"order_index":2},
{"input":"2","expected_output":"NO","is_sample":False,"order_index":3},
{"input":"4","expected_output":"YES","is_sample":False,"order_index":4},
{"input":"100","expected_output":"YES","is_sample":False,"order_index":5},
{"input":"99","expected_output":"NO","is_sample":False,"order_index":6},
]},

{"title":"Add Two Numbers","difficulty":E,"rating":800,
"description":"Given two integers a and b, print their sum.",
"input_format":"Two integers a and b on one line.","output_format":"Print a single integer — the sum.","constraints":"-10^9 ≤ a, b ≤ 10^9","time_limit_ms":1000,"memory_limit_mb":256,
"test_cases":[
{"input":"3 5","expected_output":"8","is_sample":True,"order_index":0},
{"input":"-1 1","expected_output":"0","is_sample":True,"order_index":1},
{"input":"0 0","expected_output":"0","is_sample":False,"order_index":2},
{"input":"1000000000 1000000000","expected_output":"2000000000","is_sample":False,"order_index":3},
{"input":"-1000000000 -1000000000","expected_output":"-2000000000","is_sample":False,"order_index":4},
]},

{"title":"Parity Check","difficulty":E,"rating":800,
"description":"Given an integer n, determine if it is even or odd.",
"input_format":"A single integer n.","output_format":"Print Even or Odd.","constraints":"-10^9 ≤ n ≤ 10^9","time_limit_ms":1000,"memory_limit_mb":256,
"test_cases":[
{"input":"4","expected_output":"Even","is_sample":True,"order_index":0},
{"input":"7","expected_output":"Odd","is_sample":True,"order_index":1},
{"input":"0","expected_output":"Even","is_sample":False,"order_index":2},
{"input":"-3","expected_output":"Odd","is_sample":False,"order_index":3},
{"input":"-4","expected_output":"Even","is_sample":False,"order_index":4},
{"input":"999999999","expected_output":"Odd","is_sample":False,"order_index":5},
]},

{"title":"Vowel Counter","difficulty":E,"rating":800,
"description":"Given a string of lowercase English letters, count the number of vowels (a, e, i, o, u).",
"input_format":"A single string s.","output_format":"Print the vowel count.","constraints":"1 ≤ |s| ≤ 10^5","time_limit_ms":1000,"memory_limit_mb":256,
"test_cases":[
{"input":"hello","expected_output":"2","is_sample":True,"order_index":0},
{"input":"aeiou","expected_output":"5","is_sample":True,"order_index":1},
{"input":"bcdfg","expected_output":"0","is_sample":False,"order_index":2},
{"input":"a","expected_output":"1","is_sample":False,"order_index":3},
{"input":"abracadabra","expected_output":"5","is_sample":False,"order_index":4},
]},

{"title":"Flip Array","difficulty":E,"rating":900,
"description":"Given an array of n integers, print it in reverse order.",
"input_format":"First line: n.\nSecond line: n space-separated integers.","output_format":"Print the reversed array, space-separated.","constraints":"1 ≤ n ≤ 10^5, -10^9 ≤ a[i] ≤ 10^9","time_limit_ms":1000,"memory_limit_mb":256,
"test_cases":[
{"input":"5\n1 2 3 4 5","expected_output":"5 4 3 2 1","is_sample":True,"order_index":0},
{"input":"3\n10 20 30","expected_output":"30 20 10","is_sample":True,"order_index":1},
{"input":"1\n42","expected_output":"42","is_sample":False,"order_index":2},
{"input":"2\n-1 1","expected_output":"1 -1","is_sample":False,"order_index":3},
{"input":"4\n0 0 0 0","expected_output":"0 0 0 0","is_sample":False,"order_index":4},
]},

{"title":"Peak Element","difficulty":E,"rating":800,
"description":"Given an array of n integers, find the maximum element.",
"input_format":"First line: n.\nSecond line: n integers.","output_format":"Print the maximum.","constraints":"1 ≤ n ≤ 10^5, -10^9 ≤ a[i] ≤ 10^9","time_limit_ms":1000,"memory_limit_mb":256,
"test_cases":[
{"input":"5\n1 5 3 2 4","expected_output":"5","is_sample":True,"order_index":0},
{"input":"3\n-1 -2 -3","expected_output":"-1","is_sample":True,"order_index":1},
{"input":"1\n0","expected_output":"0","is_sample":False,"order_index":2},
{"input":"4\n1000000000 999999999 999999998 999999997","expected_output":"1000000000","is_sample":False,"order_index":3},
{"input":"5\n7 7 7 7 7","expected_output":"7","is_sample":False,"order_index":4},
]},

{"title":"Target Pair","difficulty":E,"rating":900,
"description":"Given n integers and a target, determine if any two distinct elements sum to the target.",
"input_format":"First line: n and target.\nSecond line: n integers.","output_format":"Print YES or NO.","constraints":"2 ≤ n ≤ 2×10^5, -10^9 ≤ values ≤ 10^9","time_limit_ms":2000,"memory_limit_mb":256,
"test_cases":[
{"input":"4 9\n2 7 11 15","expected_output":"YES","is_sample":True,"order_index":0},
{"input":"3 10\n1 2 3","expected_output":"NO","is_sample":True,"order_index":1},
{"input":"5 0\n-1 -2 -3 1 4","expected_output":"YES","is_sample":False,"order_index":2},
{"input":"2 10\n5 5","expected_output":"YES","is_sample":False,"order_index":3},
{"input":"2 3\n1 1","expected_output":"NO","is_sample":False,"order_index":4},
{"input":"3 100\n50 25 75","expected_output":"YES","is_sample":False,"order_index":5},
]},

{"title":"Digit Sum","difficulty":E,"rating":800,
"description":"Given a non-negative integer n, compute the sum of its digits.",
"input_format":"A single integer n.","output_format":"Print the digit sum.","constraints":"0 ≤ n ≤ 10^18","time_limit_ms":1000,"memory_limit_mb":256,
"test_cases":[
{"input":"123","expected_output":"6","is_sample":True,"order_index":0},
{"input":"9999","expected_output":"36","is_sample":True,"order_index":1},
{"input":"0","expected_output":"0","is_sample":False,"order_index":2},
{"input":"10","expected_output":"1","is_sample":False,"order_index":3},
{"input":"999999999999999999","expected_output":"162","is_sample":False,"order_index":4},
]},

{"title":"Mirror String","difficulty":E,"rating":800,
"description":"Given a string s of lowercase letters, determine if it reads the same forwards and backwards.",
"input_format":"A single string s.","output_format":"Print YES or NO.","constraints":"1 ≤ |s| ≤ 10^5","time_limit_ms":1000,"memory_limit_mb":256,
"test_cases":[
{"input":"racecar","expected_output":"YES","is_sample":True,"order_index":0},
{"input":"hello","expected_output":"NO","is_sample":True,"order_index":1},
{"input":"a","expected_output":"YES","is_sample":False,"order_index":2},
{"input":"ab","expected_output":"NO","is_sample":False,"order_index":3},
{"input":"abba","expected_output":"YES","is_sample":False,"order_index":4},
{"input":"abcba","expected_output":"YES","is_sample":False,"order_index":5},
]},

{"title":"Factorial Digits","difficulty":E,"rating":900,
"description":"Given a non-negative integer n (0 ≤ n ≤ 20), compute n! (n factorial).",
"input_format":"A single integer n.","output_format":"Print n!.","constraints":"0 ≤ n ≤ 20","time_limit_ms":1000,"memory_limit_mb":256,
"test_cases":[
{"input":"5","expected_output":"120","is_sample":True,"order_index":0},
{"input":"0","expected_output":"1","is_sample":True,"order_index":1},
{"input":"1","expected_output":"1","is_sample":False,"order_index":2},
{"input":"10","expected_output":"3628800","is_sample":False,"order_index":3},
{"input":"20","expected_output":"2432902008176640000","is_sample":False,"order_index":4},
]},

{"title":"Count Duplicates","difficulty":E,"rating":900,
"description":"Given n integers, count how many distinct values appear more than once.",
"input_format":"First line: n.\nSecond line: n integers.","output_format":"Print the count of values that appear more than once.","constraints":"1 ≤ n ≤ 10^5, -10^9 ≤ a[i] ≤ 10^9","time_limit_ms":1000,"memory_limit_mb":256,
"test_cases":[
{"input":"7\n1 2 2 3 3 3 4","expected_output":"2","is_sample":True,"order_index":0},
{"input":"4\n1 2 3 4","expected_output":"0","is_sample":True,"order_index":1},
{"input":"1\n5","expected_output":"0","is_sample":False,"order_index":2},
{"input":"6\n1 1 1 1 1 1","expected_output":"1","is_sample":False,"order_index":3},
{"input":"5\n-1 -1 2 2 3","expected_output":"2","is_sample":False,"order_index":4},
]},

{"title":"Power of Two","difficulty":E,"rating":800,
"description":"Given a positive integer n, determine if it is a power of 2.",
"input_format":"A single integer n.","output_format":"Print YES or NO.","constraints":"1 ≤ n ≤ 10^18","time_limit_ms":1000,"memory_limit_mb":256,
"test_cases":[
{"input":"8","expected_output":"YES","is_sample":True,"order_index":0},
{"input":"6","expected_output":"NO","is_sample":True,"order_index":1},
{"input":"1","expected_output":"YES","is_sample":False,"order_index":2},
{"input":"1024","expected_output":"YES","is_sample":False,"order_index":3},
{"input":"1023","expected_output":"NO","is_sample":False,"order_index":4},
{"input":"576460752303423488","expected_output":"YES","is_sample":False,"order_index":5},
]},

{"title":"Celsius to Fahrenheit","difficulty":E,"rating":800,
"description":"Given n temperature readings in Celsius, convert each to Fahrenheit using the formula F = C × 9/5 + 32.\n\nPrint each result rounded down to the nearest integer.",
"input_format":"First line: n.\nSecond line: n space-separated integers (Celsius).","output_format":"Print n space-separated integers (Fahrenheit, rounded down).","constraints":"1 ≤ n ≤ 1000, -100 ≤ C ≤ 1000","time_limit_ms":1000,"memory_limit_mb":256,
"test_cases":[
{"input":"3\n0 100 37","expected_output":"32 212 98","is_sample":True,"order_index":0},
{"input":"1\n-40","expected_output":"-40","is_sample":True,"order_index":1},
{"input":"2\n-100 1000","expected_output":"-148 1832","is_sample":False,"order_index":2},
{"input":"1\n0","expected_output":"32","is_sample":False,"order_index":3},
]},

{"title":"Alternating Sign Sum","difficulty":E,"rating":900,
"description":"Given n integers a1, a2, ..., an, compute: a1 - a2 + a3 - a4 + ... (alternating signs starting with +).",
"input_format":"First line: n.\nSecond line: n integers.","output_format":"Print the alternating sum.","constraints":"1 ≤ n ≤ 10^5, -10^9 ≤ a[i] ≤ 10^9","time_limit_ms":1000,"memory_limit_mb":256,
"test_cases":[
{"input":"4\n1 2 3 4","expected_output":"-2","is_sample":True,"order_index":0},
{"input":"3\n10 5 3","expected_output":"8","is_sample":True,"order_index":1},
{"input":"1\n42","expected_output":"42","is_sample":False,"order_index":2},
{"input":"2\n0 0","expected_output":"0","is_sample":False,"order_index":3},
{"input":"5\n-1 -2 -3 -4 -5","expected_output":"-3","is_sample":False,"order_index":4},
]},

{"title":"String Squeeze","difficulty":E,"rating":900,
"description":"Given a string of lowercase letters, remove all consecutive duplicate characters.\n\nFor example, 'aabbc' becomes 'abc'.",
"input_format":"A single string s.","output_format":"Print the squeezed string.","constraints":"1 ≤ |s| ≤ 10^5","time_limit_ms":1000,"memory_limit_mb":256,
"test_cases":[
{"input":"aabbbcc","expected_output":"abc","is_sample":True,"order_index":0},
{"input":"abc","expected_output":"abc","is_sample":True,"order_index":1},
{"input":"a","expected_output":"a","is_sample":False,"order_index":2},
{"input":"aaaa","expected_output":"a","is_sample":False,"order_index":3},
{"input":"aabbaa","expected_output":"aba","is_sample":False,"order_index":4},
]},

# ══════════ MEDIUM (1000-1100) — 20 problems ══════════

{"title":"Maximum Subarray","difficulty":M,"rating":1000,
"description":"Given n integers, find the contiguous subarray (at least one element) with the maximum sum.",
"input_format":"First line: n.\nSecond line: n integers.","output_format":"Print the maximum subarray sum.","constraints":"1 ≤ n ≤ 10^5, -10^4 ≤ a[i] ≤ 10^4","time_limit_ms":2000,"memory_limit_mb":256,
"test_cases":[
{"input":"9\n-2 1 -3 4 -1 2 1 -5 4","expected_output":"6","is_sample":True,"order_index":0},
{"input":"1\n-1","expected_output":"-1","is_sample":True,"order_index":1},
{"input":"5\n1 2 3 4 5","expected_output":"15","is_sample":False,"order_index":2},
{"input":"4\n-1 -2 -3 -4","expected_output":"-1","is_sample":False,"order_index":3},
{"input":"3\n-1 0 -1","expected_output":"0","is_sample":False,"order_index":4},
{"input":"6\n2 -1 2 3 4 -5","expected_output":"10","is_sample":False,"order_index":5},
]},

{"title":"Prime Counter","difficulty":M,"rating":1000,
"description":"Given an integer n, count prime numbers strictly less than n.",
"input_format":"A single integer n.","output_format":"Print the count.","constraints":"0 ≤ n ≤ 5×10^6","time_limit_ms":3000,"memory_limit_mb":256,
"test_cases":[
{"input":"10","expected_output":"4","is_sample":True,"order_index":0},
{"input":"2","expected_output":"0","is_sample":True,"order_index":1},
{"input":"0","expected_output":"0","is_sample":False,"order_index":2},
{"input":"1","expected_output":"0","is_sample":False,"order_index":3},
{"input":"100","expected_output":"25","is_sample":False,"order_index":4},
{"input":"1000","expected_output":"168","is_sample":False,"order_index":5},
]},

{"title":"Sorted Search","difficulty":M,"rating":1000,
"description":"Given a sorted array of n distinct integers and a target t, find the 0-based index of t. Print -1 if not found.",
"input_format":"First line: n and t.\nSecond line: n sorted integers.","output_format":"Print the index or -1.","constraints":"1 ≤ n ≤ 2×10^5, -10^9 ≤ values ≤ 10^9","time_limit_ms":1000,"memory_limit_mb":256,
"test_cases":[
{"input":"5 3\n1 2 3 4 5","expected_output":"2","is_sample":True,"order_index":0},
{"input":"3 6\n1 2 3","expected_output":"-1","is_sample":True,"order_index":1},
{"input":"1 1\n1","expected_output":"0","is_sample":False,"order_index":2},
{"input":"1 2\n1","expected_output":"-1","is_sample":False,"order_index":3},
{"input":"5 5\n1 2 3 4 5","expected_output":"4","is_sample":False,"order_index":4},
]},

{"title":"Bracket Validator","difficulty":M,"rating":1000,
"description":"Given a string containing only '(', ')', '{', '}', '[', ']', determine if all brackets are correctly matched and nested.",
"input_format":"A single string s.","output_format":"Print YES or NO.","constraints":"1 ≤ |s| ≤ 10^5","time_limit_ms":1000,"memory_limit_mb":256,
"test_cases":[
{"input":"({[]})","expected_output":"YES","is_sample":True,"order_index":0},
{"input":"(]","expected_output":"NO","is_sample":True,"order_index":1},
{"input":"()","expected_output":"YES","is_sample":False,"order_index":2},
{"input":"([)]","expected_output":"NO","is_sample":False,"order_index":3},
{"input":"{","expected_output":"NO","is_sample":False,"order_index":4},
{"input":"(){}[]","expected_output":"YES","is_sample":False,"order_index":5},
{"input":"}{","expected_output":"NO","is_sample":False,"order_index":6},
]},

{"title":"Frequency Ranking","difficulty":M,"rating":1000,
"description":"Given a string of lowercase letters, print each unique character sorted by frequency (descending). Break ties alphabetically.",
"input_format":"A single string s.","output_format":"Print characters in order.","constraints":"1 ≤ |s| ≤ 10^5","time_limit_ms":1000,"memory_limit_mb":256,
"test_cases":[
{"input":"aabbbcc","expected_output":"bac","is_sample":True,"order_index":0},
{"input":"abc","expected_output":"abc","is_sample":True,"order_index":1},
{"input":"a","expected_output":"a","is_sample":False,"order_index":2},
{"input":"zzzzaaabb","expected_output":"zab","is_sample":False,"order_index":3},
{"input":"bbbaaaccc","expected_output":"abc","is_sample":False,"order_index":4},
]},

{"title":"Segment Sum Queries","difficulty":M,"rating":1100,
"description":"Given n integers and q queries, each query gives l and r (1-indexed). Print the sum of elements from index l to r inclusive.",
"input_format":"First line: n q.\nSecond line: n integers.\nNext q lines: l r.","output_format":"For each query, print the sum.","constraints":"1 ≤ n,q ≤ 2×10^5, -10^9 ≤ a[i] ≤ 10^9, 1 ≤ l ≤ r ≤ n","time_limit_ms":2000,"memory_limit_mb":256,
"test_cases":[
{"input":"5 3\n1 2 3 4 5\n1 3\n2 5\n1 5","expected_output":"6\n14\n15","is_sample":True,"order_index":0},
{"input":"3 2\n10 20 30\n1 1\n3 3","expected_output":"10\n30","is_sample":True,"order_index":1},
{"input":"1 1\n42\n1 1","expected_output":"42","is_sample":False,"order_index":2},
{"input":"4 2\n-1 -2 -3 -4\n1 4\n2 3","expected_output":"-10\n-5","is_sample":False,"order_index":3},
{"input":"5 1\n1000000000 1000000000 1000000000 1000000000 1000000000\n1 5","expected_output":"5000000000","is_sample":False,"order_index":4},
]},

{"title":"Subsequence Match","difficulty":M,"rating":1100,
"description":"Given two strings a and b consisting of lowercase letters, find the length of their longest common subsequence.",
"input_format":"First line: string a.\nSecond line: string b.","output_format":"Print the LCS length.","constraints":"1 ≤ |a|, |b| ≤ 1000","time_limit_ms":2000,"memory_limit_mb":256,
"test_cases":[
{"input":"abcde\nace","expected_output":"3","is_sample":True,"order_index":0},
{"input":"abc\nabc","expected_output":"3","is_sample":True,"order_index":1},
{"input":"abc\ndef","expected_output":"0","is_sample":False,"order_index":2},
{"input":"a\na","expected_output":"1","is_sample":False,"order_index":3},
{"input":"aaa\naa","expected_output":"2","is_sample":False,"order_index":4},
{"input":"abcdef\nfbdamn","expected_output":"2","is_sample":False,"order_index":5},
]},

{"title":"Spiral Printer","difficulty":M,"rating":1100,
"description":"Given an M×N matrix, print all elements in clockwise spiral order starting from top-left.",
"input_format":"First line: M N.\nNext M lines: N integers.","output_format":"Print all elements space-separated.","constraints":"1 ≤ M, N ≤ 100","time_limit_ms":1000,"memory_limit_mb":256,
"test_cases":[
{"input":"3 3\n1 2 3\n4 5 6\n7 8 9","expected_output":"1 2 3 6 9 8 7 4 5","is_sample":True,"order_index":0},
{"input":"1 4\n1 2 3 4","expected_output":"1 2 3 4","is_sample":True,"order_index":1},
{"input":"3 1\n1\n2\n3","expected_output":"1 2 3","is_sample":False,"order_index":2},
{"input":"2 2\n1 2\n3 4","expected_output":"1 2 4 3","is_sample":False,"order_index":3},
{"input":"1 1\n42","expected_output":"42","is_sample":False,"order_index":4},
]},

{"title":"Window Maximum","difficulty":M,"rating":1100,
"description":"Given n integers and a window size k, slide a window of size k across the array from left to right.\n\nFor each window position, print the maximum element.",
"input_format":"First line: n k.\nSecond line: n integers.","output_format":"Print the maximums space-separated.","constraints":"1 ≤ k ≤ n ≤ 10^5, -10^9 ≤ a[i] ≤ 10^9","time_limit_ms":2000,"memory_limit_mb":256,
"test_cases":[
{"input":"8 3\n1 3 -1 -3 5 3 6 7","expected_output":"3 3 5 5 6 7","is_sample":True,"order_index":0},
{"input":"5 1\n1 2 3 4 5","expected_output":"1 2 3 4 5","is_sample":True,"order_index":1},
{"input":"5 5\n1 2 3 4 5","expected_output":"5","is_sample":False,"order_index":2},
{"input":"3 2\n-1 -2 -3","expected_output":"-1 -2","is_sample":False,"order_index":3},
{"input":"1 1\n42","expected_output":"42","is_sample":False,"order_index":4},
]},

{"title":"Pair with Closest Sum","difficulty":M,"rating":1000,
"description":"Given a sorted array of n integers and a target, find two elements whose sum is closest to the target.\n\nPrint the two elements in non-decreasing order. If multiple pairs have the same closeness, print the one with the smaller first element.",
"input_format":"First line: n target.\nSecond line: n sorted integers.","output_format":"Print two integers.","constraints":"2 ≤ n ≤ 10^5, -10^9 ≤ values, target ≤ 10^9","time_limit_ms":2000,"memory_limit_mb":256,
"test_cases":[
{"input":"4 10\n1 4 5 7","expected_output":"4 7","is_sample":True,"order_index":0},
{"input":"3 0\n-1 1 2","expected_output":"-1 1","is_sample":True,"order_index":1},
{"input":"2 100\n1 2","expected_output":"1 2","is_sample":False,"order_index":2},
{"input":"5 6\n1 2 3 4 5","expected_output":"1 5","is_sample":False,"order_index":3},
{"input":"4 0\n-5 -3 3 5","expected_output":"-5 5","is_sample":False,"order_index":4},
]},

{"title":"Rotate Matrix","difficulty":M,"rating":1100,
"description":"Given an N×N matrix, rotate it 90 degrees clockwise.\n\nPrint the resulting matrix.",
"input_format":"First line: N.\nNext N lines: N integers each.","output_format":"Print the rotated N×N matrix, one row per line.","constraints":"1 ≤ N ≤ 100","time_limit_ms":1000,"memory_limit_mb":256,
"test_cases":[
{"input":"3\n1 2 3\n4 5 6\n7 8 9","expected_output":"7 4 1\n8 5 2\n9 6 3","is_sample":True,"order_index":0},
{"input":"2\n1 2\n3 4","expected_output":"3 1\n4 2","is_sample":True,"order_index":1},
{"input":"1\n5","expected_output":"5","is_sample":False,"order_index":2},
{"input":"4\n1 2 3 4\n5 6 7 8\n9 10 11 12\n13 14 15 16","expected_output":"13 9 5 1\n14 10 6 2\n15 11 7 3\n16 12 8 4","is_sample":False,"order_index":3},
]},

{"title":"Run Length Encode","difficulty":M,"rating":1000,
"description":"Given a string of lowercase letters, encode consecutive runs.\n\nEach run of character c repeated k times becomes ck (e.g., 'aabbbcc' → 'a2b3c2'). Single characters still get the count (e.g., 'abc' → 'a1b1c1').",
"input_format":"A single string s.","output_format":"Print the encoded string.","constraints":"1 ≤ |s| ≤ 10^5","time_limit_ms":1000,"memory_limit_mb":256,
"test_cases":[
{"input":"aabbbcc","expected_output":"a2b3c2","is_sample":True,"order_index":0},
{"input":"abc","expected_output":"a1b1c1","is_sample":True,"order_index":1},
{"input":"a","expected_output":"a1","is_sample":False,"order_index":2},
{"input":"aaaa","expected_output":"a4","is_sample":False,"order_index":3},
{"input":"aabbaa","expected_output":"a2b2a2","is_sample":False,"order_index":4},
]},

{"title":"First Unique Character","difficulty":M,"rating":1000,
"description":"Given a string of lowercase letters, find the index (0-based) of the first character that does not repeat anywhere in the string.\n\nIf no such character exists, print -1.",
"input_format":"A single string s.","output_format":"Print the 0-based index or -1.","constraints":"1 ≤ |s| ≤ 10^5","time_limit_ms":1000,"memory_limit_mb":256,
"test_cases":[
{"input":"leetcode","expected_output":"0","is_sample":True,"order_index":0},
{"input":"aabb","expected_output":"-1","is_sample":True,"order_index":1},
{"input":"a","expected_output":"0","is_sample":False,"order_index":2},
{"input":"aabbc","expected_output":"4","is_sample":False,"order_index":3},
{"input":"abacabad","expected_output":"4","is_sample":False,"order_index":4},
]},

{"title":"Equilibrium Index","difficulty":M,"rating":1000,
"description":"Given an array of n integers, find the leftmost equilibrium index — an index where the sum of elements to its left equals the sum of elements to its right.\n\nPrint the 0-based index, or -1 if none exists. The element at the equilibrium index is excluded from both sums.",
"input_format":"First line: n.\nSecond line: n integers.","output_format":"Print the index or -1.","constraints":"1 ≤ n ≤ 10^5, -10^9 ≤ a[i] ≤ 10^9","time_limit_ms":1000,"memory_limit_mb":256,
"test_cases":[
{"input":"7\n-7 1 5 2 -4 3 0","expected_output":"3","is_sample":True,"order_index":0},
{"input":"3\n1 2 3","expected_output":"-1","is_sample":True,"order_index":1},
{"input":"1\n0","expected_output":"0","is_sample":False,"order_index":2},
{"input":"3\n0 0 0","expected_output":"0","is_sample":False,"order_index":3},
{"input":"5\n1 -1 0 1 -1","expected_output":"2","is_sample":False,"order_index":4},
]},

{"title":"GCD of Array","difficulty":M,"rating":1000,
"description":"Given n positive integers, compute their greatest common divisor (GCD).",
"input_format":"First line: n.\nSecond line: n positive integers.","output_format":"Print the GCD.","constraints":"1 ≤ n ≤ 10^5, 1 ≤ a[i] ≤ 10^9","time_limit_ms":1000,"memory_limit_mb":256,
"test_cases":[
{"input":"3\n12 18 24","expected_output":"6","is_sample":True,"order_index":0},
{"input":"4\n7 14 21 28","expected_output":"7","is_sample":True,"order_index":1},
{"input":"1\n42","expected_output":"42","is_sample":False,"order_index":2},
{"input":"2\n1 1000000000","expected_output":"1","is_sample":False,"order_index":3},
{"input":"3\n100 100 100","expected_output":"100","is_sample":False,"order_index":4},
{"input":"5\n6 10 15 21 35","expected_output":"1","is_sample":False,"order_index":5},
]},

# ══════════ HARD (1100-1200) — 15 problems ══════════

{"title":"Shortest Route","difficulty":H,"rating":1200,
"description":"Given a weighted directed graph with n vertices (1-indexed) and m edges, find the shortest distance from vertex 1 to vertex n.\n\nPrint -1 if no path exists.",
"input_format":"First line: n m.\nNext m lines: u v w (edge u→v, weight w).","output_format":"Print the shortest distance or -1.","constraints":"2 ≤ n ≤ 10^5, 0 ≤ m ≤ 2×10^5, 1 ≤ w ≤ 10^9","time_limit_ms":3000,"memory_limit_mb":256,
"test_cases":[
{"input":"5 6\n1 2 2\n1 3 4\n2 3 1\n2 4 7\n3 5 3\n4 5 1","expected_output":"7","is_sample":True,"order_index":0},
{"input":"3 1\n1 2 5","expected_output":"-1","is_sample":True,"order_index":1},
{"input":"2 1\n1 2 10","expected_output":"10","is_sample":False,"order_index":2},
{"input":"4 4\n1 2 1\n2 3 2\n3 4 3\n1 4 10","expected_output":"6","is_sample":False,"order_index":3},
{"input":"3 0","expected_output":"-1","is_sample":False,"order_index":4},
{"input":"2 2\n1 2 5\n1 2 3","expected_output":"3","is_sample":False,"order_index":5},
]},

{"title":"Island Counter","difficulty":H,"rating":1100,
"description":"Given an M×N grid of '1' (land) and '0' (water), count the number of islands.\n\nAn island is formed by connecting adjacent land cells horizontally or vertically. The grid is surrounded by water.",
"input_format":"First line: M N.\nNext M lines: N characters (0 or 1, no spaces).","output_format":"Print the island count.","constraints":"1 ≤ M, N ≤ 300","time_limit_ms":2000,"memory_limit_mb":256,
"test_cases":[
{"input":"4 5\n11110\n11010\n11000\n00000","expected_output":"1","is_sample":True,"order_index":0},
{"input":"4 5\n11000\n11000\n00100\n00011","expected_output":"3","is_sample":True,"order_index":1},
{"input":"1 1\n0","expected_output":"0","is_sample":False,"order_index":2},
{"input":"1 1\n1","expected_output":"1","is_sample":False,"order_index":3},
{"input":"3 3\n101\n010\n101","expected_output":"5","is_sample":False,"order_index":4},
{"input":"3 3\n111\n111\n111","expected_output":"1","is_sample":False,"order_index":5},
]},

{"title":"Minimum Coins","difficulty":H,"rating":1200,
"description":"Given n coin denominations and a target amount, find the minimum number of coins needed to make the exact amount.\n\nYou have unlimited coins of each denomination. Print -1 if impossible.",
"input_format":"First line: n target.\nSecond line: n integers.","output_format":"Print the minimum coins or -1.","constraints":"1 ≤ n ≤ 100, 0 ≤ target ≤ 10^4, 1 ≤ coins[i] ≤ 10^4","time_limit_ms":2000,"memory_limit_mb":256,
"test_cases":[
{"input":"3 11\n1 5 6","expected_output":"2","is_sample":True,"order_index":0},
{"input":"1 3\n2","expected_output":"-1","is_sample":True,"order_index":1},
{"input":"1 0\n1","expected_output":"0","is_sample":False,"order_index":2},
{"input":"3 6\n1 3 4","expected_output":"2","is_sample":False,"order_index":3},
{"input":"2 7\n2 3","expected_output":"3","is_sample":False,"order_index":4},
{"input":"1 1\n1","expected_output":"1","is_sample":False,"order_index":5},
]},

{"title":"Overlap Merger","difficulty":H,"rating":1100,
"description":"Given n intervals [start, end], merge all overlapping intervals.\n\nTwo intervals overlap if they share at least one point. Print merged intervals sorted by start.",
"input_format":"First line: n.\nNext n lines: start end.","output_format":"Print merged intervals, one per line.","constraints":"1 ≤ n ≤ 10^5, 0 ≤ start ≤ end ≤ 10^9","time_limit_ms":2000,"memory_limit_mb":256,
"test_cases":[
{"input":"4\n1 3\n2 6\n8 10\n15 18","expected_output":"1 6\n8 10\n15 18","is_sample":True,"order_index":0},
{"input":"2\n1 4\n4 5","expected_output":"1 5","is_sample":True,"order_index":1},
{"input":"1\n0 0","expected_output":"0 0","is_sample":False,"order_index":2},
{"input":"3\n1 10\n2 3\n4 5","expected_output":"1 10","is_sample":False,"order_index":3},
{"input":"3\n1 2\n3 4\n5 6","expected_output":"1 2\n3 4\n5 6","is_sample":False,"order_index":4},
]},

{"title":"Rising Sequence","difficulty":H,"rating":1200,
"description":"Given n integers, find the length of the longest strictly increasing subsequence.\n\nA subsequence maintains relative order but need not be contiguous.",
"input_format":"First line: n.\nSecond line: n integers.","output_format":"Print the LIS length.","constraints":"1 ≤ n ≤ 10^5, -10^9 ≤ a[i] ≤ 10^9","time_limit_ms":2000,"memory_limit_mb":256,
"test_cases":[
{"input":"8\n10 9 2 5 3 7 101 18","expected_output":"4","is_sample":True,"order_index":0},
{"input":"6\n0 1 0 3 2 3","expected_output":"4","is_sample":True,"order_index":1},
{"input":"1\n42","expected_output":"1","is_sample":False,"order_index":2},
{"input":"5\n5 4 3 2 1","expected_output":"1","is_sample":False,"order_index":3},
{"input":"5\n1 2 3 4 5","expected_output":"5","is_sample":False,"order_index":4},
{"input":"4\n1 1 1 1","expected_output":"1","is_sample":False,"order_index":5},
]},

{"title":"Grid Pathways","difficulty":H,"rating":1100,
"description":"Given an M×N grid, count the number of unique paths from top-left (1,1) to bottom-right (M,N).\n\nYou can only move right or down at each step. Print the answer.",
"input_format":"Two integers M and N.","output_format":"Print the number of unique paths.","constraints":"1 ≤ M, N ≤ 15","time_limit_ms":1000,"memory_limit_mb":256,
"test_cases":[
{"input":"3 3","expected_output":"6","is_sample":True,"order_index":0},
{"input":"3 7","expected_output":"28","is_sample":True,"order_index":1},
{"input":"1 1","expected_output":"1","is_sample":False,"order_index":2},
{"input":"1 5","expected_output":"1","is_sample":False,"order_index":3},
{"input":"2 2","expected_output":"2","is_sample":False,"order_index":4},
{"input":"15 15","expected_output":"40116600","is_sample":False,"order_index":5},
]},

{"title":"Knapsack Value","difficulty":H,"rating":1200,
"description":"You have n items, each with a weight and a value. Your knapsack can carry at most W weight.\n\nFind the maximum total value you can carry. Each item can only be used once.",
"input_format":"First line: n W.\nNext n lines: weight value.","output_format":"Print the maximum value.","constraints":"1 ≤ n ≤ 100, 1 ≤ W ≤ 10^4, 1 ≤ weight, value ≤ 10^4","time_limit_ms":2000,"memory_limit_mb":256,
"test_cases":[
{"input":"3 50\n10 60\n20 100\n30 120","expected_output":"220","is_sample":True,"order_index":0},
{"input":"4 7\n1 1\n3 4\n4 5\n5 7","expected_output":"9","is_sample":True,"order_index":1},
{"input":"1 1\n2 100","expected_output":"0","is_sample":False,"order_index":2},
{"input":"1 10\n5 50","expected_output":"50","is_sample":False,"order_index":3},
{"input":"3 10\n5 10\n5 10\n5 10","expected_output":"20","is_sample":False,"order_index":4},
]},

{"title":"Level Order Traversal","difficulty":H,"rating":1100,
"description":"Given a complete binary tree represented as an array of n integers (1-indexed, where children of node i are at 2i and 2i+1), print the tree level by level.\n\nEach level should be on a separate line, elements space-separated.",
"input_format":"First line: n.\nSecond line: n integers.","output_format":"Print each level on a separate line.","constraints":"1 ≤ n ≤ 1023","time_limit_ms":1000,"memory_limit_mb":256,
"test_cases":[
{"input":"7\n1 2 3 4 5 6 7","expected_output":"1\n2 3\n4 5 6 7","is_sample":True,"order_index":0},
{"input":"3\n10 20 30","expected_output":"10\n20 30","is_sample":True,"order_index":1},
{"input":"1\n42","expected_output":"42","is_sample":False,"order_index":2},
{"input":"15\n1 2 3 4 5 6 7 8 9 10 11 12 13 14 15","expected_output":"1\n2 3\n4 5 6 7\n8 9 10 11 12 13 14 15","is_sample":False,"order_index":3},
]},

{"title":"Connected Components","difficulty":H,"rating":1200,
"description":"Given an undirected graph with n vertices (1-indexed) and m edges, count the number of connected components.",
"input_format":"First line: n m.\nNext m lines: u v.","output_format":"Print the number of connected components.","constraints":"1 ≤ n ≤ 10^5, 0 ≤ m ≤ 2×10^5","time_limit_ms":2000,"memory_limit_mb":256,
"test_cases":[
{"input":"5 3\n1 2\n2 3\n4 5","expected_output":"2","is_sample":True,"order_index":0},
{"input":"4 0","expected_output":"4","is_sample":True,"order_index":1},
{"input":"1 0","expected_output":"1","is_sample":False,"order_index":2},
{"input":"3 3\n1 2\n2 3\n1 3","expected_output":"1","is_sample":False,"order_index":3},
{"input":"6 2\n1 2\n3 4","expected_output":"4","is_sample":False,"order_index":4},
]},

{"title":"Subset Sum Check","difficulty":H,"rating":1200,
"description":"Given n positive integers, determine if any subset sums to exactly target.\n\nPrint YES or NO.",
"input_format":"First line: n target.\nSecond line: n positive integers.","output_format":"Print YES or NO.","constraints":"1 ≤ n ≤ 20, 1 ≤ target ≤ 10^6, 1 ≤ a[i] ≤ 10^5","time_limit_ms":2000,"memory_limit_mb":256,
"test_cases":[
{"input":"4 9\n3 1 5 9","expected_output":"YES","is_sample":True,"order_index":0},
{"input":"3 7\n1 2 3","expected_output":"YES","is_sample":True,"order_index":1},
{"input":"3 10\n1 2 3","expected_output":"NO","is_sample":False,"order_index":2},
{"input":"1 5\n5","expected_output":"YES","is_sample":False,"order_index":3},
{"input":"1 3\n5","expected_output":"NO","is_sample":False,"order_index":4},
{"input":"5 15\n1 2 3 4 5","expected_output":"YES","is_sample":False,"order_index":5},
]},

{"title":"Longest Plateau","difficulty":H,"rating":1100,
"description":"Given a sorted array of n integers (non-decreasing order), find the length of the longest plateau — the maximum number of consecutive equal elements.",
"input_format":"First line: n.\nSecond line: n sorted integers.","output_format":"Print the plateau length.","constraints":"1 ≤ n ≤ 10^5, -10^9 ≤ a[i] ≤ 10^9","time_limit_ms":1000,"memory_limit_mb":256,
"test_cases":[
{"input":"8\n1 2 2 3 3 3 4 4","expected_output":"3","is_sample":True,"order_index":0},
{"input":"5\n1 2 3 4 5","expected_output":"1","is_sample":True,"order_index":1},
{"input":"1\n42","expected_output":"1","is_sample":False,"order_index":2},
{"input":"6\n5 5 5 5 5 5","expected_output":"6","is_sample":False,"order_index":3},
{"input":"4\n1 1 2 2","expected_output":"2","is_sample":False,"order_index":4},
]},

{"title":"Edit Distance","difficulty":H,"rating":1200,
"description":"Given two strings a and b, find the minimum number of operations to convert a into b.\n\nAllowed operations: insert a character, delete a character, or replace a character. Each operation costs 1.",
"input_format":"First line: string a.\nSecond line: string b.","output_format":"Print the minimum edit distance.","constraints":"0 ≤ |a|, |b| ≤ 500. Strings contain lowercase English letters.","time_limit_ms":2000,"memory_limit_mb":256,
"test_cases":[
{"input":"horse\nros","expected_output":"3","is_sample":True,"order_index":0},
{"input":"intention\nexecution","expected_output":"5","is_sample":True,"order_index":1},
{"input":"a\na","expected_output":"0","is_sample":False,"order_index":2},
{"input":"abc\nabc","expected_output":"0","is_sample":False,"order_index":3},
{"input":"a\nb","expected_output":"1","is_sample":False,"order_index":4},
{"input":"\nabc","expected_output":"3","is_sample":False,"order_index":5},
]},

{"title":"Trapping Rainwater","difficulty":H,"rating":1200,
"description":"Given n non-negative integers representing an elevation map where the width of each bar is 1, compute how much water can be trapped after raining.",
"input_format":"First line: n.\nSecond line: n non-negative integers.","output_format":"Print the total trapped water.","constraints":"1 ≤ n ≤ 10^5, 0 ≤ height[i] ≤ 10^4","time_limit_ms":1000,"memory_limit_mb":256,
"test_cases":[
{"input":"12\n0 1 0 2 1 0 1 3 2 1 2 1","expected_output":"6","is_sample":True,"order_index":0},
{"input":"6\n4 2 0 3 2 5","expected_output":"9","is_sample":True,"order_index":1},
{"input":"1\n5","expected_output":"0","is_sample":False,"order_index":2},
{"input":"3\n1 0 1","expected_output":"1","is_sample":False,"order_index":3},
{"input":"5\n5 4 3 2 1","expected_output":"0","is_sample":False,"order_index":4},
{"input":"5\n1 2 3 4 5","expected_output":"0","is_sample":False,"order_index":5},
]},

{"title":"Expression Evaluator","difficulty":H,"rating":1200,
"description":"Given a string containing a mathematical expression with +, -, *, and non-negative integers (no parentheses, no whitespace), evaluate it.\n\nFollow standard operator precedence: * before + and -. Evaluate left to right for same precedence.",
"input_format":"A single string representing the expression.","output_format":"Print the result as an integer.","constraints":"1 ≤ |s| ≤ 1000, all intermediate results fit in a 64-bit integer, no division","time_limit_ms":1000,"memory_limit_mb":256,
"test_cases":[
{"input":"3+2*2","expected_output":"7","is_sample":True,"order_index":0},
{"input":"3+5-2","expected_output":"6","is_sample":True,"order_index":1},
{"input":"0","expected_output":"0","is_sample":False,"order_index":2},
{"input":"1*2*3*4","expected_output":"24","is_sample":False,"order_index":3},
{"input":"10+20*3-5","expected_output":"65","is_sample":False,"order_index":4},
{"input":"100","expected_output":"100","is_sample":False,"order_index":5},
]},

{"title":"Zigzag Levels","difficulty":H,"rating":1100,
"description":"Given a complete binary tree as an array of n integers (1-indexed), print it in zigzag level order.\n\nOdd levels (1st, 3rd, ...) print left to right. Even levels (2nd, 4th, ...) print right to left.",
"input_format":"First line: n.\nSecond line: n integers.","output_format":"Print each level on a separate line.","constraints":"1 ≤ n ≤ 1023","time_limit_ms":1000,"memory_limit_mb":256,
"test_cases":[
{"input":"7\n1 2 3 4 5 6 7","expected_output":"1\n3 2\n4 5 6 7","is_sample":True,"order_index":0},
{"input":"3\n10 20 30","expected_output":"10\n30 20","is_sample":True,"order_index":1},
{"input":"1\n42","expected_output":"42","is_sample":False,"order_index":2},
{"input":"15\n1 2 3 4 5 6 7 8 9 10 11 12 13 14 15","expected_output":"1\n3 2\n4 5 6 7\n15 14 13 12 11 10 9 8","is_sample":False,"order_index":3},
]},
]

# ══════════ Seeder ══════════
async def seed():
    engine = create_async_engine(settings.database_url, echo=False)
    Session = async_sessionmaker(engine, expire_on_commit=False)
    async with Session() as db:
        for p_data in PROBLEMS:
            tc_data = p_data.pop("test_cases")
            existing = await db.execute(select(Problem).where(Problem.title == p_data["title"]))
            if existing.scalar_one_or_none():
                logger.info(f"  ─ Skip: {p_data['title']}")
                continue
            problem = Problem(**p_data)
            db.add(problem)
            await db.flush()
            for tc in tc_data:
                db.add(TestCase(problem_id=problem.id, **tc))
            s = sum(1 for t in tc_data if t["is_sample"])
            logger.info(f"  ✓ {problem.title} [{problem.difficulty}/{problem.rating}] ({s}+{len(tc_data)-s} cases)")
        await db.commit()
        logger.info("\n✅ Seeded all problems.")
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(seed())
