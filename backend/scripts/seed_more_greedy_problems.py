import asyncio
import heapq
import random

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.config import settings
from backend.core.constants import Difficulty
from backend.scripts.array_seed_utils import make_case, upsert_problem

MOD = 10**9 + 7
TARGET_CASES = 440


def solve_assign_cookies(greed: list[int], cookies: list[int]) -> int:
    greed = sorted(greed)
    cookies = sorted(cookies)
    child = cookie = 0
    while child < len(greed) and cookie < len(cookies):
        if cookies[cookie] >= greed[child]:
            child += 1
        cookie += 1
    return child


def build_assign_cookies_cases() -> list[dict]:
    cases, idx = [], 0
    for greed, cookies, expected in [([1, 2, 3], [1, 1], 1), ([1, 2], [1, 2, 3], 2)]:
        cases.append(make_case(greed, cookies, expected_output=expected, idx=idx, is_sample=True))
        idx += 1
    fixed = [
        ([], [], 0), ([1], [], 0), ([], [1, 2], 0), ([1], [1], 1), ([5, 6, 7], [1, 2, 3], 0),
        ([1, 1, 1], [1, 1], 2), ([2, 2, 3], [3, 3, 3], 3), ([10, 9, 8, 7], [5, 6, 7, 8], 2),
        ([1, 2, 2, 3], [2, 2, 2], 3), ([4, 5, 6], [7, 8, 9], 3),
    ]
    for greed, cookies, expected in fixed:
        cases.append(make_case(greed, cookies, expected_output=expected, idx=idx))
        idx += 1
    rng = random.Random(2026040301)
    while len(cases) < TARGET_CASES:
        greed = [rng.randint(1, 25) for _ in range(rng.randint(0, 140))]
        cookies = [rng.randint(1, 25) for _ in range(rng.randint(0, 160))]
        cases.append(make_case(greed, cookies, expected_output=solve_assign_cookies(greed, cookies), idx=idx))
        idx += 1
    return cases


def solve_lemonade_change(bills: list[int]) -> bool:
    five = ten = 0
    for bill in bills:
        if bill == 5:
            five += 1
        elif bill == 10:
            if five == 0:
                return False
            five -= 1
            ten += 1
        else:
            if ten > 0 and five > 0:
                ten -= 1
                five -= 1
            elif five >= 3:
                five -= 3
            else:
                return False
    return True


def build_lemonade_change_cases() -> list[dict]:
    cases, idx = [], 0
    for bills, expected in [([5, 5, 5, 10, 20], True), ([5, 5, 10, 10, 20], False)]:
        cases.append(make_case(bills, expected_output=expected, idx=idx, is_sample=True))
        idx += 1
    fixed = [
        ([5], True), ([10], False), ([20], False), ([5, 10], True), ([5, 20], False),
        ([5, 5, 20], False), ([5, 5, 5, 20], True), ([5, 5, 10, 20], True), ([5, 10, 5, 20], False),
        ([5, 5, 5, 10, 5, 20, 5, 10, 20], True),
    ]
    for bills, expected in fixed:
        cases.append(make_case(bills, expected_output=expected, idx=idx))
        idx += 1
    rng = random.Random(2026040302)
    while len(cases) < TARGET_CASES:
        bills = [rng.choice([5, 10, 20]) for _ in range(rng.randint(1, 180))]
        cases.append(make_case(bills, expected_output=solve_lemonade_change(bills), idx=idx))
        idx += 1
    return cases


def solve_can_place_flowers(flowerbed: list[int], n: int) -> bool:
    flowerbed = flowerbed[:]
    planted = 0
    for i in range(len(flowerbed)):
        if flowerbed[i] == 1:
            continue
        left = i == 0 or flowerbed[i - 1] == 0
        right = i == len(flowerbed) - 1 or flowerbed[i + 1] == 0
        if left and right:
            flowerbed[i] = 1
            planted += 1
            if planted >= n:
                return True
    return planted >= n


def build_can_place_flowers_cases() -> list[dict]:
    cases, idx = [], 0
    for bed, n, expected in [([1, 0, 0, 0, 1], 1, True), ([1, 0, 0, 0, 1], 2, False)]:
        cases.append(make_case(bed, n, expected_output=expected, idx=idx, is_sample=True))
        idx += 1
    fixed = [
        ([0], 1, True), ([1], 0, True), ([1], 1, False), ([0, 0], 1, True), ([0, 0], 2, False),
        ([0, 0, 0], 2, True), ([1, 0, 0, 0, 0], 2, True), ([0, 0, 0, 1, 0, 0, 0], 2, True),
        ([0, 1, 0, 1, 0], 1, False), ([0, 0, 0, 0, 0], 3, True),
    ]
    for bed, n, expected in fixed:
        cases.append(make_case(bed, n, expected_output=expected, idx=idx))
        idx += 1
    rng = random.Random(2026040303)
    while len(cases) < TARGET_CASES:
        length = rng.randint(1, 160)
        bed = [0] * length
        for i in range(length):
            if rng.random() < 0.2 and bed[i] == 0 and (i == 0 or bed[i - 1] == 0) and (i == length - 1 or bed[i + 1] == 0):
                bed[i] = 1
        n = rng.randint(0, max(1, length // 2 + 2))
        cases.append(make_case(bed, n, expected_output=solve_can_place_flowers(bed, n), idx=idx))
        idx += 1
    return cases


def solve_task_scheduler(tasks: list[str], n: int) -> int:
    counts = {}
    for task in tasks:
        counts[task] = counts.get(task, 0) + 1
    max_freq = max(counts.values(), default=0)
    max_count = sum(1 for value in counts.values() if value == max_freq)
    return max(len(tasks), (max_freq - 1) * (n + 1) + max_count)


def build_task_scheduler_cases() -> list[dict]:
    cases, idx = [], 0
    for tasks, n, expected in [(["A", "A", "A", "B", "B", "B"], 2, 8), (["A", "C", "A", "B", "D", "B"], 1, 6)]:
        cases.append(make_case(tasks, n, expected_output=expected, idx=idx, is_sample=True))
        idx += 1
    fixed = [
        ([], 3, 0), (["A"], 0, 1), (["A", "A", "A"], 2, 7), (["A", "B", "C"], 5, 3),
        (["A", "A", "B", "B"], 2, 5), (["A", "A", "A", "B", "B", "B"], 50, 104),
        (["A", "A", "A", "B", "C", "D"], 2, 7), (["A", "A", "B", "B", "C", "C", "D", "D"], 3, 8),
    ]
    for tasks, n, expected in fixed:
        cases.append(make_case(tasks, n, expected_output=expected, idx=idx))
        idx += 1
    rng = random.Random(2026040305)
    alphabet = [chr(ord("A") + i) for i in range(8)]
    while len(cases) < TARGET_CASES:
        tasks = [rng.choice(alphabet) for _ in range(rng.randint(0, 180))]
        n = rng.randint(0, 15)
        cases.append(make_case(tasks, n, expected_output=solve_task_scheduler(tasks, n), idx=idx))
        idx += 1
    return cases


def solve_min_arrows(points: list[list[int]]) -> int:
    if not points:
        return 0
    ordered = sorted(points, key=lambda item: item[1])
    arrows, end = 1, ordered[0][1]
    for start, finish in ordered[1:]:
        if start > end:
            arrows += 1
            end = finish
    return arrows


def build_min_arrows_cases() -> list[dict]:
    cases, idx = [], 0
    for points, expected in [([[10, 16], [2, 8], [1, 6], [7, 12]], 2), ([[1, 2], [3, 4], [5, 6], [7, 8]], 4)]:
        cases.append(make_case(points, expected_output=expected, idx=idx, is_sample=True))
        idx += 1
    fixed = [
        ([], 0), ([[1, 2]], 1), ([[1, 5], [2, 3], [3, 4]], 1), ([[1, 2], [2, 3], [3, 4]], 2),
        ([[-5, -1], [-4, 0], [1, 2]], 2), ([[1, 10], [2, 9], [3, 8], [4, 7]], 1),
        ([[0, 0], [0, 1], [1, 1]], 2), ([[2, 3], [2, 3], [2, 3]], 1),
    ]
    for points, expected in fixed:
        cases.append(make_case(points, expected_output=expected, idx=idx))
        idx += 1
    rng = random.Random(2026040307)
    while len(cases) < TARGET_CASES:
        points = []
        for _ in range(rng.randint(0, 160)):
            left = rng.randint(-1000, 1000)
            points.append([left, rng.randint(left, left + rng.randint(0, 80))])
        cases.append(make_case(points, expected_output=solve_min_arrows(points), idx=idx))
        idx += 1
    return cases


def solve_bag_of_tokens(tokens: list[int], power: int) -> int:
    tokens = sorted(tokens)
    left, right, score, best = 0, len(tokens) - 1, 0, 0
    while left <= right:
        if power >= tokens[left]:
            power -= tokens[left]
            score += 1
            best = max(best, score)
            left += 1
        elif score > 0 and left < right:
            power += tokens[right]
            score -= 1
            right -= 1
        else:
            break
    return best


def build_bag_of_tokens_cases() -> list[dict]:
    cases, idx = [], 0
    for tokens, power, expected in [([100], 50, 0), ([100, 200, 300, 400], 200, 2)]:
        cases.append(make_case(tokens, power, expected_output=expected, idx=idx, is_sample=True))
        idx += 1
    fixed = [
        ([], 100, 0), ([50], 50, 1), ([50], 49, 0), ([25, 25, 25], 75, 3),
        ([10, 200], 150, 1), ([100, 200, 300], 250, 2), ([1, 2, 3, 4], 2, 2), ([40, 40, 40, 40], 80, 2),
    ]
    for tokens, power, expected in fixed:
        cases.append(make_case(tokens, power, expected_output=expected, idx=idx))
        idx += 1
    rng = random.Random(2026040308)
    while len(cases) < TARGET_CASES:
        tokens = [rng.randint(1, 400) for _ in range(rng.randint(0, 120))]
        power = rng.randint(0, 800)
        cases.append(make_case(tokens, power, expected_output=solve_bag_of_tokens(tokens, power), idx=idx))
        idx += 1
    return cases


def solve_course_schedule_iii(courses: list[list[int]]) -> int:
    total, taken = 0, []
    for duration, end in sorted(courses, key=lambda item: item[1]):
        total += duration
        heapq.heappush(taken, -duration)
        if total > end:
            total += heapq.heappop(taken)
    return len(taken)


def build_course_schedule_iii_cases() -> list[dict]:
    cases, idx = [], 0
    for courses, expected in [([[100, 200], [200, 1300], [1000, 1250], [2000, 3200]], 3), ([[1, 2]], 1)]:
        cases.append(make_case(courses, expected_output=expected, idx=idx, is_sample=True))
        idx += 1
    fixed = [
        ([], 0), ([[3, 2]], 0), ([[1, 2], [2, 3]], 1), ([[5, 5], [4, 6], [2, 6]], 2),
        ([[5, 5], [5, 6], [5, 7]], 1), ([[1, 10], [2, 10], [3, 10], [4, 10]], 4),
        ([[100, 200], [50, 100], [150, 400], [200, 500]], 3), ([[5, 15], [5, 16], [5, 17], [5, 18]], 3),
    ]
    for courses, expected in fixed:
        cases.append(make_case(courses, expected_output=expected, idx=idx))
        idx += 1
    rng = random.Random(2026040309)
    while len(cases) < TARGET_CASES:
        courses = []
        for _ in range(rng.randint(0, 140)):
            duration = rng.randint(1, 60)
            courses.append([duration, rng.randint(duration, duration + 250)])
        cases.append(make_case(courses, expected_output=solve_course_schedule_iii(courses), idx=idx))
        idx += 1
    return cases


def solve_min_refuel_stops(target: int, start_fuel: int, stations: list[list[int]]) -> int:
    fuel, idx, used, best = start_fuel, 0, 0, []
    while fuel < target:
        while idx < len(stations) and stations[idx][0] <= fuel:
            heapq.heappush(best, -stations[idx][1])
            idx += 1
        if not best:
            return -1
        fuel += -heapq.heappop(best)
        used += 1
    return used


def build_min_refuel_cases() -> list[dict]:
    cases, idx = [], 0
    for target, start_fuel, stations, expected in [(1, 1, [], 0), (100, 10, [[10, 60], [20, 30], [30, 30], [60, 40]], 2)]:
        cases.append(make_case(target, start_fuel, stations, expected_output=expected, idx=idx, is_sample=True))
        idx += 1
    fixed = [
        (100, 1, [], -1), (50, 60, [], 0), (100, 50, [[25, 25], [50, 25]], 2), (100, 50, [[60, 50]], -1),
        (100, 10, [[10, 90]], 1), (100, 25, [[25, 25], [50, 25], [75, 25]], 3), (200, 100, [[50, 25], [100, 100]], 1),
        (100, 99, [[99, 1]], 1),
    ]
    for target, start_fuel, stations, expected in fixed:
        cases.append(make_case(target, start_fuel, stations, expected_output=expected, idx=idx))
        idx += 1
    rng = random.Random(2026040310)
    while len(cases) < TARGET_CASES:
        stations, position = [], 0
        for _ in range(rng.randint(0, 80)):
            position += rng.randint(1, 20)
            stations.append([position, rng.randint(1, 120)])
        target = position + rng.randint(1, 120)
        start_fuel = rng.randint(1, 120)
        cases.append(make_case(target, start_fuel, stations, expected_output=solve_min_refuel_stops(target, start_fuel, stations), idx=idx))
        idx += 1
    return cases


def solve_max_performance(n: int, speed: list[int], efficiency: list[int], k: int) -> int:
    team_speed, answer, heap = 0, 0, []
    for eff, spd in sorted(zip(efficiency, speed), reverse=True):
        heapq.heappush(heap, spd)
        team_speed += spd
        if len(heap) > k:
            team_speed -= heapq.heappop(heap)
        answer = max(answer, team_speed * eff)
    return answer % MOD


def build_max_performance_cases() -> list[dict]:
    cases, idx = [], 0
    for n, speed, efficiency, k, expected in [
        (6, [2, 10, 3, 1, 5, 8], [5, 4, 3, 9, 7, 2], 2, 60),
        (6, [2, 10, 3, 1, 5, 8], [5, 4, 3, 9, 7, 2], 3, 68),
    ]:
        cases.append(make_case(n, speed, efficiency, k, expected_output=expected, idx=idx, is_sample=True))
        idx += 1
    fixed = [
        (1, [5], [7], 1, 35), (3, [2, 8, 2], [2, 7, 1], 1, 56), (4, [10, 10, 10, 10], [1, 2, 3, 4], 2, 60),
        (5, [5, 5, 5, 5, 5], [5, 5, 5, 5, 5], 3, 75), (3, [7, 7, 7], [3, 3, 3], 2, 42),
        (4, [4, 2, 3, 1], [8, 7, 6, 5], 2, 42),
    ]
    for n, speed, efficiency, k, expected in fixed:
        cases.append(make_case(n, speed, efficiency, k, expected_output=expected, idx=idx))
        idx += 1
    rng = random.Random(2026040311)
    while len(cases) < TARGET_CASES:
        n = rng.randint(1, 120)
        speed = [rng.randint(1, 1000) for _ in range(n)]
        efficiency = [rng.randint(1, 1000) for _ in range(n)]
        k = rng.randint(1, n)
        cases.append(make_case(n, speed, efficiency, k, expected_output=solve_max_performance(n, speed, efficiency, k), idx=idx))
        idx += 1
    return cases


def solve_ipo(k: int, w: int, profits: list[int], capital: list[int]) -> int:
    projects = sorted(zip(capital, profits))
    idx, current, available = 0, w, []
    for _ in range(k):
        while idx < len(projects) and projects[idx][0] <= current:
            heapq.heappush(available, -projects[idx][1])
            idx += 1
        if not available:
            break
        current += -heapq.heappop(available)
    return current


def build_ipo_cases() -> list[dict]:
    cases, idx = [], 0
    for k, w, profits, capital, expected in [(2, 0, [1, 2, 3], [0, 1, 1], 4), (3, 0, [1, 2, 3], [0, 1, 2], 6)]:
        cases.append(make_case(k, w, profits, capital, expected_output=expected, idx=idx, is_sample=True))
        idx += 1
    fixed = [
        (0, 10, [1, 2], [0, 0], 10), (2, 0, [], [], 0), (1, 0, [5], [1], 0), (1, 1, [5], [1], 6),
        (2, 1, [1, 2, 3], [1, 1, 2], 6), (3, 2, [1, 1, 1], [0, 1, 2], 5), (4, 0, [1, 2, 3, 4], [0, 0, 0, 0], 10),
        (5, 0, [2, 2, 2], [0, 1, 2], 6),
    ]
    for k, w, profits, capital, expected in fixed:
        cases.append(make_case(k, w, profits, capital, expected_output=expected, idx=idx))
        idx += 1
    rng = random.Random(2026040312)
    while len(cases) < TARGET_CASES:
        n = rng.randint(0, 120)
        k = rng.randint(0, 50)
        w = rng.randint(0, 150)
        profits = [rng.randint(0, 100) for _ in range(n)]
        capital = [rng.randint(0, 150) for _ in range(n)]
        cases.append(make_case(k, w, profits, capital, expected_output=solve_ipo(k, w, profits, capital), idx=idx))
        idx += 1
    return cases


PROBLEMS = [
    ("Assign Cookies", build_assign_cookies_cases, dict(description="Assume you are an awesome parent and want to give your children cookies. Each child has a greed factor and each cookie has a size. Return the maximum number of content children.", difficulty=Difficulty.EASY, input_format="Line 1: JSON array g\nLine 2: JSON array s", output_format="Integer count of satisfied children", constraints="0 <= g.length, s.length <= 300\n1 <= g[i], s[j] <= 10^3", method_name="findContentChildren", parameters=[{"name": "g", "type": "int[]"}, {"name": "s", "type": "int[]"}], return_type="int", time_limit_ms=1500, memory_limit_mb=256, rating=900, is_active=True)),
    ("Lemonade Change", build_lemonade_change_cases, dict(description="Each lemonade costs $5. Customers pay in order with 5, 10, or 20 dollar bills. Return true if you can provide every customer with the correct change.", difficulty=Difficulty.EASY, input_format="Line 1: JSON array bills", output_format="Boolean true/false", constraints="1 <= bills.length <= 10^5\nbills[i] is 5, 10, or 20", method_name="lemonadeChange", parameters=[{"name": "bills", "type": "int[]"}], return_type="bool", time_limit_ms=1500, memory_limit_mb=256, rating=900, is_active=True)),
    ("Can Place Flowers", build_can_place_flowers_cases, dict(description="You have a flowerbed where adjacent flowers cannot both be planted. Return true if n new flowers can be planted without violating the rule.", difficulty=Difficulty.EASY, input_format="Line 1: JSON array flowerbed\nLine 2: integer n", output_format="Boolean true/false", constraints="1 <= flowerbed.length <= 2 * 10^4\nflowerbed[i] is 0 or 1\n0 <= n <= flowerbed.length", method_name="canPlaceFlowers", parameters=[{"name": "flowerbed", "type": "int[]"}, {"name": "n", "type": "int"}], return_type="bool", time_limit_ms=1500, memory_limit_mb=256, rating=900, is_active=True)),
    ("Task Scheduler", build_task_scheduler_cases, dict(description="You are given CPU tasks represented by letters and a cooling interval n. Return the least number of intervals needed to finish all tasks.", difficulty=Difficulty.MEDIUM, input_format="Line 1: JSON array tasks\nLine 2: integer n", output_format="Integer least interval count", constraints="0 <= tasks.length <= 10^4\n0 <= n <= 100\ntasks[i] is an uppercase English letter.", method_name="leastInterval", parameters=[{"name": "tasks", "type": "string[]"}, {"name": "n", "type": "int"}], return_type="int", time_limit_ms=1500, memory_limit_mb=256, rating=1150, is_active=True)),
    ("Minimum Number of Arrows to Burst Balloons", build_min_arrows_cases, dict(description="An arrow shot at x bursts every balloon interval with start <= x <= end. Return the minimum number of arrows needed to burst all balloons.", difficulty=Difficulty.MEDIUM, input_format="Line 1: JSON matrix points", output_format="Integer minimum arrows needed", constraints="0 <= points.length <= 10^5\n-2^31 <= xstart <= xend <= 2^31 - 1", method_name="findMinArrowShots", parameters=[{"name": "points", "type": "int[][]"}], return_type="int", time_limit_ms=1500, memory_limit_mb=256, rating=1200, is_active=True)),
    ("Bag of Tokens", build_bag_of_tokens_cases, dict(description="You start with power and a bag of tokens. Spending power can gain score, and spending score can gain power. Return the maximum score achievable.", difficulty=Difficulty.MEDIUM, input_format="Line 1: JSON array tokens\nLine 2: integer power", output_format="Integer maximum score", constraints="0 <= tokens.length <= 1000\n0 <= tokens[i], power <= 10^4", method_name="bagOfTokensScore", parameters=[{"name": "tokens", "type": "int[]"}, {"name": "power", "type": "int"}], return_type="int", time_limit_ms=1500, memory_limit_mb=256, rating=1250, is_active=True)),
    ("Course Schedule III", build_course_schedule_iii_cases, dict(description="Each course has a duration and a closing day. Return the maximum number of courses that can be taken.", difficulty=Difficulty.HARD, input_format="Line 1: JSON matrix courses", output_format="Integer maximum courses taken", constraints="0 <= courses.length <= 10^4\n1 <= durationi, lastDayi <= 10^4", method_name="scheduleCourse", parameters=[{"name": "courses", "type": "int[][]"}], return_type="int", time_limit_ms=1800, memory_limit_mb=256, rating=1450, is_active=True)),
    ("Minimum Number of Refueling Stops", build_min_refuel_cases, dict(description="A car starts with startFuel and needs to reach target miles. Return the minimum number of refueling stops needed, or -1 if impossible.", difficulty=Difficulty.HARD, input_format="Line 1: integer target\nLine 2: integer startFuel\nLine 3: JSON matrix stations", output_format="Integer minimum refuel stops, or -1", constraints="1 <= target <= 10^9\n1 <= startFuel <= 10^9\n0 <= stations.length <= 500\n1 <= fueli <= 10^9", method_name="minRefuelStops", parameters=[{"name": "target", "type": "int"}, {"name": "startFuel", "type": "int"}, {"name": "stations", "type": "int[][]"}], return_type="int", time_limit_ms=1800, memory_limit_mb=256, rating=1500, is_active=True)),
    ("Maximum Performance of a Team", build_max_performance_cases, dict(description="Choose at most k engineers with given speed and efficiency to maximize team performance. Return the answer modulo 1e9 + 7.", difficulty=Difficulty.HARD, input_format="Line 1: integer n\nLine 2: JSON array speed\nLine 3: JSON array efficiency\nLine 4: integer k", output_format="Integer maximum performance modulo 1e9+7", constraints="1 <= n <= 10^5\n1 <= speed[i], efficiency[i] <= 10^8\n1 <= k <= n", method_name="maxPerformance", parameters=[{"name": "n", "type": "int"}, {"name": "speed", "type": "int[]"}, {"name": "efficiency", "type": "int[]"}, {"name": "k", "type": "int"}], return_type="int", time_limit_ms=2000, memory_limit_mb=256, rating=1550, is_active=True)),
    ("IPO", build_ipo_cases, dict(description="You may complete at most k projects, but can only start projects whose capital requirement you can afford. Return the maximized capital after at most k projects.", difficulty=Difficulty.HARD, input_format="Line 1: integer k\nLine 2: integer w\nLine 3: JSON array profits\nLine 4: JSON array capital", output_format="Integer final capital", constraints="0 <= k <= 10^5\n0 <= w <= 10^9\n0 <= profits.length == capital.length <= 10^5\n0 <= profits[i], capital[i] <= 10^9", method_name="findMaximizedCapital", parameters=[{"name": "k", "type": "int"}, {"name": "w", "type": "int"}, {"name": "profits", "type": "int[]"}, {"name": "capital", "type": "int[]"}], return_type="int", time_limit_ms=2000, memory_limit_mb=256, rating=1600, is_active=True)),
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
