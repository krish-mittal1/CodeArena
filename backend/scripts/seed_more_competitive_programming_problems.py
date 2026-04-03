from __future__ import annotations

import asyncio
import math
import random
from dataclasses import dataclass
from typing import Callable

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.config import settings
from backend.core.constants import Difficulty
from backend.scripts.cp_seed_utils import make_case, upsert_problem

TARGET_CASES = 480


def _clean_lines(data: str) -> list[str]:
    return [line.strip() for line in data.strip().splitlines() if line.strip() or line == ""]


def _first_ints(data: str) -> list[int]:
    return list(map(int, data.split()))


def _case_list(
    solver: Callable[[str], str],
    samples: list[str],
    edges: list[str],
    random_factory: Callable[[random.Random], str],
    seed: int,
) -> list[dict]:
    cases: list[dict] = []
    idx = 0
    for sample in samples:
        cases.append(make_case(sample, solver(sample), idx, is_sample=True))
        idx += 1
    for edge in edges:
        cases.append(make_case(edge, solver(edge), idx))
        idx += 1

    rng = random.Random(seed)
    while len(cases) < TARGET_CASES:
        payload = random_factory(rng)
        cases.append(make_case(payload, solver(payload), idx))
        idx += 1
    return cases


def _render_constraints(*lines: str) -> str:
    return "\n".join(lines)


@dataclass(frozen=True)
class CPProblemSpec:
    title: str
    description: str
    difficulty: str
    rating: int
    input_format: str
    output_format: str
    constraints: str
    samples: list[str]
    edges: list[str]
    solver: Callable[[str], str]
    random_factory: Callable[[random.Random], str]
    seed: int


def solve_domino_piling(data: str) -> str:
    m, n = map(int, data.split())
    return str((m * n) // 2)


def random_domino_piling(rng: random.Random) -> str:
    return f"{rng.randint(1, 16)} {rng.randint(1, 16)}"


def solve_beautiful_matrix(data: str) -> str:
    rows = [list(map(int, line.split())) for line in _clean_lines(data)]
    for i in range(5):
        for j in range(5):
            if rows[i][j] == 1:
                return str(abs(i - 2) + abs(j - 2))
    return "0"


def random_beautiful_matrix(rng: random.Random) -> str:
    pos = rng.randint(0, 24)
    rows = []
    for i in range(5):
        row = []
        for j in range(5):
            row.append("1" if i * 5 + j == pos else "0")
        rows.append(" ".join(row))
    return "\n".join(rows)


def solve_bitpp(data: str) -> str:
    lines = _clean_lines(data)
    n = int(lines[0])
    value = 0
    for op in lines[1:n + 1]:
        value += 1 if "+" in op else -1
    return str(value)


def random_bitpp(rng: random.Random) -> str:
    n = rng.randint(1, 60)
    ops = [rng.choice(["++X", "X++", "--X", "X--"]) for _ in range(n)]
    return "\n".join([str(n), *ops])


def solve_boy_or_girl(data: str) -> str:
    name = data.strip()
    return "CHAT WITH HER!" if len(set(name)) % 2 == 0 else "IGNORE HIM!"


def random_boy_or_girl(rng: random.Random) -> str:
    length = rng.randint(1, 100)
    letters = [chr(ord("a") + rng.randint(0, 25)) for _ in range(length)]
    return "".join(letters)


def solve_petya_strings(data: str) -> str:
    a, b = _clean_lines(data)[:2]
    a = a.lower()
    b = b.lower()
    if a < b:
        return "-1"
    if a > b:
        return "1"
    return "0"


def random_petya_strings(rng: random.Random) -> str:
    length = rng.randint(1, 30)
    a = "".join(chr(ord("A") + rng.randint(0, 25)) if rng.random() < 0.5 else chr(ord("a") + rng.randint(0, 25)) for _ in range(length))
    b = "".join(chr(ord("A") + rng.randint(0, 25)) if rng.random() < 0.5 else chr(ord("a") + rng.randint(0, 25)) for _ in range(length))
    return f"{a}\n{b}"


def solve_word(data: str) -> str:
    s = data.strip()
    upper = sum(1 for ch in s if ch.isupper())
    lower = len(s) - upper
    return s.lower() if lower >= upper else s.upper()


def random_word(rng: random.Random) -> str:
    length = rng.randint(1, 100)
    chars = []
    for _ in range(length):
        base = chr(ord("a") + rng.randint(0, 25))
        chars.append(base.upper() if rng.random() < 0.45 else base)
    return "".join(chars)


def solve_bear_big_brother(data: str) -> str:
    a, b = map(int, data.split())
    years = 0
    while a <= b:
        a *= 3
        b *= 2
        years += 1
    return str(years)


def random_bear_big_brother(rng: random.Random) -> str:
    a = rng.randint(1, 10)
    b = rng.randint(a, 10)
    return f"{a} {b}"


def solve_wrong_subtraction(data: str) -> str:
    n, k = map(int, data.split())
    for _ in range(k):
        if n % 10 == 0:
            n //= 10
        else:
            n -= 1
    return str(n)


def random_wrong_subtraction(rng: random.Random) -> str:
    n = rng.randint(1, 10**9)
    k = rng.randint(1, 50)
    return f"{n} {k}"


def solve_elephant(data: str) -> str:
    x = int(data.strip())
    return str((x + 4) // 5)


def random_elephant(rng: random.Random) -> str:
    return str(rng.randint(1, 1_000_000))


def solve_stones_on_table(data: str) -> str:
    lines = _clean_lines(data)
    n = int(lines[0])
    s = lines[1][:n]
    return str(sum(1 for i in range(1, len(s)) if s[i] == s[i - 1]))


def random_stones_on_table(rng: random.Random) -> str:
    n = rng.randint(1, 120)
    s = "".join(rng.choice("RGB") for _ in range(n))
    return f"{n}\n{s}"


def solve_nearly_lucky(data: str) -> str:
    count = sum(1 for ch in data.strip() if ch in {"4", "7"})
    return "YES" if str(count) and set(str(count)) <= {"4", "7"} else "NO"


def random_nearly_lucky(rng: random.Random) -> str:
    length = rng.randint(1, 18)
    digits = "".join(str(rng.randint(0, 9)) for _ in range(length))
    return digits


def solve_anton_and_danik(data: str) -> str:
    lines = _clean_lines(data)
    s = lines[1][: int(lines[0])]
    a = s.count("A")
    d = s.count("D")
    if a > d:
        return "Anton"
    if d > a:
        return "Danik"
    return "Friendship"


def random_anton_and_danik(rng: random.Random) -> str:
    n = rng.randint(1, 100)
    s = "".join(rng.choice("AD") for _ in range(n))
    return f"{n}\n{s}"


def solve_beautiful_year(data: str) -> str:
    year = int(data.strip()) + 1
    while len(set(str(year))) != 4:
        year += 1
    return str(year)


def random_beautiful_year(rng: random.Random) -> str:
    return str(rng.randint(1000, 8999))


def solve_soldier_and_bananas(data: str) -> str:
    k, n, w = map(int, data.split())
    total = k * w * (w + 1) // 2
    return str(max(0, total - n))


def random_soldier_and_bananas(rng: random.Random) -> str:
    return f"{rng.randint(1, 1000)} {rng.randint(0, 10**7)} {rng.randint(1, 1000)}"


def solve_tram(data: str) -> str:
    lines = _clean_lines(data)
    n = int(lines[0])
    cur = 0
    best = 0
    for line in lines[1:n + 1]:
        a, b = map(int, line.split())
        cur -= a
        cur += b
        best = max(best, cur)
    return str(best)


def random_tram(rng: random.Random) -> str:
    n = rng.randint(1, 60)
    cur = 0
    lines = [str(n)]
    for _ in range(n):
        leave = rng.randint(0, cur)
        enter = rng.randint(0, 30)
        cur = cur - leave + enter
        lines.append(f"{leave} {enter}")
    return "\n".join(lines)


def solve_george_accommodation(data: str) -> str:
    lines = _clean_lines(data)
    n = int(lines[0])
    count = 0
    for line in lines[1:n + 1]:
        p, q = map(int, line.split())
        if q - p >= 2:
            count += 1
    return str(count)


def random_george_accommodation(rng: random.Random) -> str:
    n = rng.randint(1, 80)
    lines = [str(n)]
    for _ in range(n):
        q = rng.randint(1, 10)
        p = rng.randint(0, q)
        lines.append(f"{p} {q}")
    return "\n".join(lines)


def solve_easy_problem(data: str) -> str:
    values = _first_ints(data)
    opinions = values[1:]
    return "HARD" if any(opinions) else "EASY"


def random_easy_problem(rng: random.Random) -> str:
    n = rng.randint(1, 100)
    arr = [str(rng.randint(0, 1)) for _ in range(n)]
    return f"{n}\n{' '.join(arr)}"


def solve_hq9(data: str) -> str:
    return "YES" if any(ch in "HQ9" for ch in data.strip()) else "NO"


def random_hq9(rng: random.Random) -> str:
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+-"
    length = rng.randint(1, 120)
    return "".join(rng.choice(alphabet) for _ in range(length))


def solve_horseshoe(data: str) -> str:
    values = list(map(int, data.split()))
    return str(4 - len(set(values)))


def random_horseshoe(rng: random.Random) -> str:
    return " ".join(str(rng.randint(1, 10**6)) for _ in range(4))


def solve_calculating_function(data: str) -> str:
    n = int(data.strip())
    return str(n // 2 if n % 2 == 0 else -(n + 1) // 2)


def random_calculating_function(rng: random.Random) -> str:
    return str(rng.randint(1, 10**15))


def solve_vanya_fence(data: str) -> str:
    values = _first_ints(data)
    n, h = values[0], values[1]
    widths = values[2:2 + n]
    return str(sum(2 if x > h else 1 for x in widths))


def random_vanya_fence(rng: random.Random) -> str:
    n = rng.randint(1, 100)
    h = rng.randint(1, 1000)
    arr = [str(rng.randint(1, 2 * h + 20)) for _ in range(n)]
    return f"{n} {h}\n{' '.join(arr)}"


def solve_translation(data: str) -> str:
    s, t = _clean_lines(data)[:2]
    return "YES" if s[::-1] == t else "NO"


def random_translation(rng: random.Random) -> str:
    length = rng.randint(1, 100)
    s = "".join(chr(ord("a") + rng.randint(0, 25)) for _ in range(length))
    if rng.random() < 0.5:
        t = s[::-1]
    else:
        t = "".join(chr(ord("a") + rng.randint(0, 25)) for _ in range(length))
    return f"{s}\n{t}"


def solve_even_odds(data: str) -> str:
    n, k = map(int, data.split())
    odd_count = (n + 1) // 2
    if k <= odd_count:
        return str(2 * k - 1)
    return str(2 * (k - odd_count))


def random_even_odds(rng: random.Random) -> str:
    n = rng.randint(1, 10**12)
    k = rng.randint(1, n)
    return f"{n} {k}"


PROBLEMS: list[CPProblemSpec] = [
    CPProblemSpec(
        title="Domino Piling",
        description="A board of size m x n is given. Find the maximum number of 2 x 1 dominoes that can be placed on the board so that no two dominoes overlap.",
        difficulty=Difficulty.EASY,
        rating=800,
        input_format="The first line contains two integers m and n — the board dimensions.",
        output_format="Print one integer — the maximum number of dominoes that can be placed.",
        constraints=_render_constraints("1 <= m <= 16", "1 <= n <= 16"),
        samples=["2 4", "3 3"],
        edges=["1 1", "1 16", "16 1", "2 2", "15 15", "16 16", "3 4", "7 8", "9 10", "11 13", "14 15", "5 5"],
        solver=solve_domino_piling,
        random_factory=random_domino_piling,
        seed=1101,
    ),
    CPProblemSpec(
        title="Beautiful Matrix",
        description="A 5 x 5 matrix contains exactly one number 1 and all other numbers are 0. In one move you can swap neighboring rows or columns. Find the minimum number of moves required to bring 1 to the center.",
        difficulty=Difficulty.EASY,
        rating=800,
        input_format="Five lines follow, each containing five integers 0 or 1.",
        output_format="Print the minimum number of moves needed to bring 1 to position (3, 3).",
        constraints=_render_constraints("The matrix size is fixed at 5 x 5.", "Exactly one cell contains 1."),
        samples=[
            "0 0 0 0 0\n0 0 0 0 0\n0 0 0 1 0\n0 0 0 0 0\n0 0 0 0 0",
            "0 0 0 0 0\n0 0 0 0 0\n0 1 0 0 0\n0 0 0 0 0\n0 0 0 0 0",
        ],
        edges=[random_beautiful_matrix(random.Random(i)) for i in range(12, 24)],
        solver=solve_beautiful_matrix,
        random_factory=random_beautiful_matrix,
        seed=1102,
    ),
    CPProblemSpec(
        title="Bit++",
        description="You are given a variable X initially equal to 0 and a list of statements. Each statement increments or decrements X by 1. Print the final value of X.",
        difficulty=Difficulty.EASY,
        rating=800,
        input_format="The first line contains an integer n. Each of the next n lines contains one statement.",
        output_format="Print one integer — the final value of X.",
        constraints=_render_constraints("1 <= n <= 150", "Each statement is one of ++X, X++, --X, X--."),
        samples=["1\n++X", "2\nX++\n--X"],
        edges=["1\n--X", "3\n++X\n++X\n++X", "4\nX--\nX--\nX++\n++X", "5\n++X\nX++\n--X\nX--\n++X", "2\nX--\nX--", "6\n++X\n++X\nX++\n--X\nX--\nX++", "7\nX++\nX++\nX++\nX++\nX++\nX++\nX++", "8\n--X\n--X\n--X\n--X\n--X\n--X\n--X\n--X", "9\n++X\nX--\n++X\nX--\n++X\nX--\n++X\nX--\n++X", "10\nX++\nX--\nX++\nX--\nX++\nX--\nX++\nX--\nX++\nX--", "12\n++X\n++X\n++X\n--X\n--X\nX++\nX--\nX++\nX--\nX++\nX--\n++X", "15\nX++\nX++\nX++\nX++\n--X\n--X\n--X\n++X\n++X\nX--\nX--\nX++\n--X\n++X\nX++"],
        solver=solve_bitpp,
        random_factory=random_bitpp,
        seed=1103,
    ),
    CPProblemSpec(
        title="Boy or Girl",
        description="Count how many distinct letters are in the username. If the number is even, print CHAT WITH HER!, otherwise print IGNORE HIM!.",
        difficulty=Difficulty.EASY,
        rating=800,
        input_format="The only line contains a non-empty username consisting of lowercase English letters.",
        output_format='Print "CHAT WITH HER!" if the number of distinct characters is even, otherwise print "IGNORE HIM!".',
        constraints=_render_constraints("1 <= |username| <= 100"),
        samples=["wjmzbmr", "xiaodao", "sevenkplus"],
        edges=["a", "aa", "ab", "abc", "abcd", "zzzzzz", "abababab", "qwerty", "hello", "competitive", "programming", "abcdefghijklmnopqrstuvwxyz"],
        solver=solve_boy_or_girl,
        random_factory=random_boy_or_girl,
        seed=1104,
    ),
    CPProblemSpec(
        title="Petya and Strings",
        description="Compare two strings lexicographically, ignoring the difference between uppercase and lowercase letters.",
        difficulty=Difficulty.EASY,
        rating=800,
        input_format="The first line contains string a. The second line contains string b.",
        output_format='Print "-1" if a < b, "1" if a > b, and "0" if they are equal after converting both to lowercase.',
        constraints=_render_constraints("1 <= |a| = |b| <= 100", "The strings contain English letters only."),
        samples=["aaaa\naaaA", "abs\nAbz", "abcdefg\nAbCdEfF"],
        edges=["A\na", "Z\na", "abc\nabd", "ABC\nABB", "zzz\nZZZ", "Hello\nhELLo", "Apple\napric", "xYz\nXya", "LongString\nlongstring", "Case\nbase", "MiXeD\nmixed", "Alpha\nALPHB"],
        solver=solve_petya_strings,
        random_factory=random_petya_strings,
        seed=1105,
    ),
    CPProblemSpec(
        title="Word",
        description="Convert the word to all lowercase if it contains at least as many lowercase letters as uppercase letters. Otherwise convert it to all uppercase.",
        difficulty=Difficulty.EASY,
        rating=800,
        input_format="The only line contains a word consisting of uppercase and lowercase Latin letters.",
        output_format="Print the transformed word.",
        constraints=_render_constraints("1 <= |word| <= 100"),
        samples=["HoUse", "ViP", "maTRIx"],
        edges=["A", "a", "ABC", "abc", "AbCd", "zzZZ", "AAAAaaaa", "MixedCaseWord", "XyZ", "lOwer", "UPPER", "AaAaAaAa"],
        solver=solve_word,
        random_factory=random_word,
        seed=1106,
    ),
    CPProblemSpec(
        title="Bear and Big Brother",
        description="Two bears have weights a and b. Every year Limak's weight triples and Bob's weight doubles. Find how many years it takes for Limak to become strictly heavier than Bob.",
        difficulty=Difficulty.EASY,
        rating=800,
        input_format="The first line contains two integers a and b.",
        output_format="Print the number of years after which a becomes greater than b.",
        constraints=_render_constraints("1 <= a <= b <= 10"),
        samples=["4 7", "4 9", "1 1"],
        edges=["1 2", "1 10", "2 2", "2 3", "3 9", "5 5", "6 10", "8 9", "9 9", "10 10", "7 8", "4 10"],
        solver=solve_bear_big_brother,
        random_factory=random_bear_big_brother,
        seed=1107,
    ),
    CPProblemSpec(
        title="Wrong Subtraction",
        description="Perform k operations on n. In one operation, if the last digit of n is zero, divide it by 10; otherwise subtract 1 from n.",
        difficulty=Difficulty.EASY,
        rating=800,
        input_format="The first line contains two integers n and k.",
        output_format="Print the resulting value of n after k operations.",
        constraints=_render_constraints("2 <= n <= 10^9", "1 <= k <= 50"),
        samples=["512 4", "1000000000 9"],
        edges=["10 1", "10 2", "9 1", "9 8", "100 3", "101 1", "109 2", "1000 5", "999999999 1", "1000000000 10", "11 10", "500 12"],
        solver=solve_wrong_subtraction,
        random_factory=random_wrong_subtraction,
        seed=1108,
    ),
    CPProblemSpec(
        title="Elephant",
        description="An elephant wants to move exactly x steps forward. In one move it can move 1, 2, 3, 4, or 5 steps. Find the minimum number of moves.",
        difficulty=Difficulty.EASY,
        rating=800,
        input_format="The only line contains an integer x.",
        output_format="Print the minimum number of moves.",
        constraints=_render_constraints("1 <= x <= 10^6"),
        samples=["5", "12"],
        edges=["1", "2", "3", "4", "5", "6", "9", "10", "11", "999999", "1000000", "123456"],
        solver=solve_elephant,
        random_factory=random_elephant,
        seed=1109,
    ),
    CPProblemSpec(
        title="Stones on the Table",
        description="There are n stones in a row, each colored R, G, or B. Count how many stones must be removed so that no two neighboring stones have the same color.",
        difficulty=Difficulty.EASY,
        rating=800,
        input_format="The first line contains integer n. The second line contains a string s of length n.",
        output_format="Print the minimum number of stones to remove.",
        constraints=_render_constraints("1 <= n <= 50", "s contains only characters R, G, and B."),
        samples=["3\nRRG", "5\nRRRRR", "4\nBRBG"],
        edges=["1\nR", "2\nRR", "2\nRG", "3\nRGB", "4\nRRGG", "5\nRGRGR", "6\nBBBBBB", "7\nRGBRGBR", "8\nRRGGBBRR", "9\nGRRRRRRRG", "10\nRGBBBBRRRR", "12\nRRGBGBBRRGGB"],
        solver=solve_stones_on_table,
        random_factory=random_stones_on_table,
        seed=1110,
    ),
    CPProblemSpec(
        title="Nearly Lucky Number",
        description="A number is nearly lucky if the count of digits 4 and 7 in it is itself a lucky number. Determine whether the given number is nearly lucky.",
        difficulty=Difficulty.EASY,
        rating=800,
        input_format="The only line contains the integer n.",
        output_format='Print "YES" if n is nearly lucky, otherwise print "NO".',
        constraints=_render_constraints("1 <= n <= 10^18"),
        samples=["40047", "7747774", "1000000000000000000"],
        edges=["4", "7", "44", "47", "74", "77", "123456", "4444", "7777777", "447700", "987654321", "4747474747"],
        solver=solve_nearly_lucky,
        random_factory=random_nearly_lucky,
        seed=1111,
    ),
    CPProblemSpec(
        title="Anton and Danik",
        description="Anton and Danik played n games. Each result is recorded as A or D. Determine who won more games, or print Friendship if they won the same number.",
        difficulty=Difficulty.EASY,
        rating=800,
        input_format="The first line contains integer n. The second line contains a string of length n consisting of A and D.",
        output_format='Print "Anton", "Danik", or "Friendship".',
        constraints=_render_constraints("1 <= n <= 1000"),
        samples=["6\nADAAAA", "7\nDDDAADA", "6\nDADADA"],
        edges=["1\nA", "1\nD", "2\nAD", "2\nAA", "2\nDD", "3\nADA", "4\nAADD", "5\nDDDDA", "6\nAAAADD", "7\nADADADA", "8\nDDDAAAAD", "10\nAADDAADDAD"],
        solver=solve_anton_and_danik,
        random_factory=random_anton_and_danik,
        seed=1112,
    ),
    CPProblemSpec(
        title="Beautiful Year",
        description="Find the smallest year strictly greater than y such that all digits of the year are distinct.",
        difficulty=Difficulty.EASY,
        rating=800,
        input_format="The only line contains integer y.",
        output_format="Print the next beautiful year.",
        constraints=_render_constraints("1000 <= y <= 9000"),
        samples=["1987", "2013"],
        edges=["1000", "1111", "1234", "1989", "2001", "2011", "5555", "8765", "8798", "8978", "8999", "9012"],
        solver=solve_beautiful_year,
        random_factory=random_beautiful_year,
        seed=1113,
    ),
    CPProblemSpec(
        title="Soldier and Bananas",
        description="The cost of the first banana is k dollars, the second is 2k, and so on. If the soldier has n dollars and wants to buy w bananas, compute how much money he must borrow.",
        difficulty=Difficulty.EASY,
        rating=800,
        input_format="The first line contains three integers k, n, and w.",
        output_format="Print the amount of money the soldier needs to borrow. If he needs nothing, print 0.",
        constraints=_render_constraints("1 <= k <= 1000", "0 <= n <= 10^9", "1 <= w <= 1000"),
        samples=["3 17 4", "4 10 4"],
        edges=["1 0 1", "1 1 1", "2 3 1", "2 3 2", "1000 0 1000", "10 100 10", "7 300 20", "5 1000 50", "13 13 13", "8 500 30", "9 45 9", "100 100000 100"],
        solver=solve_soldier_and_bananas,
        random_factory=random_soldier_and_bananas,
        seed=1114,
    ),
    CPProblemSpec(
        title="Tram",
        description="A tram has n stops. At each stop some passengers leave and some enter. Determine the minimum capacity that the tram must have so that all passengers fit during the whole route.",
        difficulty=Difficulty.EASY,
        rating=800,
        input_format="The first line contains n. Each of the next n lines contains two integers a and b — the number of passengers that leave and enter.",
        output_format="Print the minimum required capacity of the tram.",
        constraints=_render_constraints("2 <= n <= 1000", "0 <= a, b <= 1000"),
        samples=["4\n0 3\n2 5\n4 2\n4 0", "2\n0 2\n2 0"],
        edges=["1\n0 1", "2\n0 5\n5 0", "3\n0 2\n1 1\n2 0", "4\n0 1\n0 1\n1 0\n1 0", "5\n0 10\n3 5\n4 2\n5 1\n6 0", "6\n0 3\n1 2\n2 4\n3 3\n4 2\n5 0", "7\n0 7\n1 0\n1 3\n3 2\n2 1\n4 0\n3 0", "3\n0 1000\n500 0\n500 0", "4\n0 1\n1 2\n2 3\n3 4", "5\n0 5\n2 4\n3 1\n1 3\n7 0", "6\n0 6\n2 3\n3 2\n1 4\n5 1\n4 0", "8\n0 2\n0 2\n1 1\n1 3\n2 0\n2 4\n4 1\n5 0"],
        solver=solve_tram,
        random_factory=random_tram,
        seed=1115,
    ),
    CPProblemSpec(
        title="George and Accommodation",
        description="There are n rooms in a dormitory. Each room currently has p people and can hold q people. Count how many rooms have room for at least two more people.",
        difficulty=Difficulty.EASY,
        rating=800,
        input_format="The first line contains n. Each of the next n lines contains two integers p and q.",
        output_format="Print the number of rooms that can accommodate at least two more people.",
        constraints=_render_constraints("1 <= n <= 100", "0 <= p <= q <= 100"),
        samples=["3\n1 1\n2 2\n3 3", "3\n1 10\n0 10\n10 10"],
        edges=["1\n0 2", "1\n1 2", "1\n2 2", "2\n0 3\n1 2", "3\n1 3\n2 4\n3 5", "4\n0 1\n1 2\n2 3\n3 4", "5\n0 5\n3 5\n2 4\n4 4\n1 2", "6\n1 10\n8 10\n0 2\n2 2\n3 7\n5 6", "7\n0 0\n0 1\n0 2\n0 3\n0 4\n0 5\n0 6", "8\n1 3\n2 3\n3 5\n4 4\n1 5\n2 2\n6 10\n9 10", "9\n0 10\n1 2\n2 4\n3 7\n4 5\n5 8\n6 6\n7 9\n8 10", "10\n0 2\n1 3\n2 4\n3 5\n4 6\n5 7\n6 8\n7 9\n8 10\n9 11"],
        solver=solve_george_accommodation,
        random_factory=random_george_accommodation,
        seed=1116,
    ),
    CPProblemSpec(
        title="In Search of an Easy Problem",
        description="The team asked n people whether a problem is hard. If at least one person says 1, the problem is hard. Otherwise it is easy.",
        difficulty=Difficulty.EASY,
        rating=800,
        input_format="The first line contains n. The second line contains n integers 0 or 1.",
        output_format='Print "HARD" if at least one opinion is 1, otherwise print "EASY".',
        constraints=_render_constraints("1 <= n <= 100"),
        samples=["3\n0 0 1", "1\n0"],
        edges=["1\n1", "2\n0 0", "2\n1 0", "3\n0 0 0", "3\n1 1 1", "4\n0 1 0 1", "5\n0 0 0 0 0", "6\n1 0 0 0 0 0", "7\n0 0 0 0 0 0 1", "8\n1 1 0 0 1 0 0 1", "9\n0 1 0 1 0 1 0 1 0", "10\n0 0 1 0 0 1 0 0 1 0"],
        solver=solve_easy_problem,
        random_factory=random_easy_problem,
        seed=1117,
    ),
    CPProblemSpec(
        title="HQ9+",
        description="A program is given as a string. If it contains the characters H, Q, or 9, the program outputs something. Determine whether this happens.",
        difficulty=Difficulty.EASY,
        rating=900,
        input_format="The only line contains the program string.",
        output_format='Print "YES" if the program will produce output, otherwise print "NO".',
        constraints=_render_constraints("1 <= |program| <= 100"),
        samples=["Hi!", "Codeforces", "Q9+"],
        edges=["H", "Q", "9", "+", "++++", "abc", "hello", "QQQQ", "999", "HQ", "h9", "A1B2C3"],
        solver=solve_hq9,
        random_factory=random_hq9,
        seed=1118,
    ),
    CPProblemSpec(
        title="Is your horseshoe on the other hoof?",
        description="You have four horseshoes. Compute how many horseshoes you need to buy so that all four have distinct colors.",
        difficulty=Difficulty.EASY,
        rating=800,
        input_format="The only line contains four integers s1, s2, s3, and s4.",
        output_format="Print the number of horseshoes to buy.",
        constraints=_render_constraints("1 <= s_i <= 10^9"),
        samples=["1 7 3 3", "7 7 7 7"],
        edges=["1 2 3 4", "1 1 1 1", "1 1 2 3", "1 2 2 3", "1 2 3 3", "5 5 6 6", "10 20 10 20", "100 200 300 400", "7 8 7 8", "9 9 10 10", "11 12 13 11", "999 1000 1001 1002"],
        solver=solve_horseshoe,
        random_factory=random_horseshoe,
        seed=1119,
    ),
    CPProblemSpec(
        title="Calculating Function",
        description="For a positive integer n, define f(n) = 1 - 2 + 3 - 4 + ... ± n. Print the value of f(n).",
        difficulty=Difficulty.EASY,
        rating=800,
        input_format="The only line contains integer n.",
        output_format="Print the value of f(n).",
        constraints=_render_constraints("1 <= n <= 10^15"),
        samples=["4", "5"],
        edges=["1", "2", "3", "4", "5", "10", "11", "999999999999999", "1000000000000000", "123456789", "222222222", "777777777777"],
        solver=solve_calculating_function,
        random_factory=random_calculating_function,
        seed=1120,
    ),
    CPProblemSpec(
        title="Vanya and Fence",
        description="A group of friends wants to walk in one row through a fence of height h. Each person of height greater than h needs width 2, otherwise width 1. Find the minimum width of the road.",
        difficulty=Difficulty.EASY,
        rating=800,
        input_format="The first line contains integers n and h. The second line contains n integers a1 ... an.",
        output_format="Print the minimum required width.",
        constraints=_render_constraints("1 <= n <= 1000", "1 <= h <= 1000", "1 <= a_i <= 2 * 10^3"),
        samples=["3 7\n4 5 14", "6 1\n1 1 1 1 1 1"],
        edges=["1 1\n1", "1 1\n2", "2 3\n1 3", "2 3\n4 5", "3 5\n5 5 5", "4 5\n6 1 5 10", "5 10\n11 12 13 14 15", "6 4\n1 2 3 4 5 6", "7 7\n7 7 7 8 8 6 5", "8 2\n3 3 3 3 3 3 3 3", "9 9\n1 2 3 4 5 6 7 8 9", "10 6\n6 7 6 7 6 7 6 7 6 7"],
        solver=solve_vanya_fence,
        random_factory=random_vanya_fence,
        seed=1121,
    ),
    CPProblemSpec(
        title="Translation",
        description="Check whether the second string is equal to the reverse of the first string.",
        difficulty=Difficulty.EASY,
        rating=800,
        input_format="The first line contains string s. The second line contains string t.",
        output_format='Print "YES" if t is the reverse of s, otherwise print "NO".',
        constraints=_render_constraints("1 <= |s| = |t| <= 100"),
        samples=["code\nedoc", "abb\naba"],
        edges=["a\na", "ab\nba", "ab\nab", "abc\ncba", "abcd\ndcba", "hello\nolleh", "level\nlevel", "mirror\nrorrim", "xyz\nzyx", "reverse\nesrever", "aaaa\naaaa", "abcd\ndcbb"],
        solver=solve_translation,
        random_factory=random_translation,
        seed=1122,
    ),
    CPProblemSpec(
        title="Even Odds",
        description="Write down all odd numbers from 1 to n, then all even numbers from 1 to n. Find the k-th number in that order.",
        difficulty=Difficulty.MEDIUM,
        rating=900,
        input_format="The only line contains two integers n and k.",
        output_format="Print the k-th number in the described sequence.",
        constraints=_render_constraints("1 <= k <= n <= 10^12"),
        samples=["10 3", "7 7"],
        edges=["1 1", "2 1", "2 2", "3 2", "4 3", "5 5", "6 6", "7 1", "7 4", "8 8", "999999999999 1", "1000000000000 1000000000000"],
        solver=solve_even_odds,
        random_factory=random_even_odds,
        seed=1123,
    ),
]


async def seed() -> None:
    engine = create_async_engine(settings.database_url, echo=False)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as db:
        for spec in PROBLEMS:
            await upsert_problem(
                db,
                spec.title,
                dict(
                    description=spec.description,
                    difficulty=spec.difficulty,
                    input_format=spec.input_format,
                    output_format=spec.output_format,
                    constraints=spec.constraints,
                    problem_type="cp",
                    time_limit_ms=1000,
                    memory_limit_mb=256,
                    rating=spec.rating,
                    is_active=True,
                ),
                _case_list(spec.solver, spec.samples, spec.edges, spec.random_factory, spec.seed),
            )
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
