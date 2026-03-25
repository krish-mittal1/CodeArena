#!/usr/bin/env python3
"""
Massive Seed script: 
- 100 problems across 5 categories
- 1000 test cases per problem (100,000 total)
- Includes topic in the description
- Uses asyncpg executemany for high speed batch inserts

Run inside the api container:
  docker exec api sh -c 'cd /app && .venv/bin/python /app/seed_100_problems.py'
Or locally if ports are exposed:
  python seed_100_problems.py
"""

import asyncio
import uuid
import asyncpg
import random
import string
import os

db_url = os.environ.get("DATABASE_URL", "postgresql://postgres:krishisunique@localhost:5432/codexarena")
# If running inside docker, the host is usually api_postgres
# We can try to use standard config if the script fails, but user is likely running it locally.
PROBLEMS = []

# --- 1. Math Problems (20) ---
def make_math_gen(k):
    def _gen():
        random.seed(k * 100)
        cases = []
        cases.append(("0", "YES"))
        cases.append((str(k), "YES"))
        cases.append((str(-k), "YES"))
        cases.append(("1", "NO" if k!=1 else "YES"))
        for _ in range(996):
            if random.random() < 0.2:
                n = random.randint(-1000, 1000) * k
            else:
                n = random.randint(-1_000_000_000, 1_000_000_000)
            cases.append((str(n), "YES" if n % k == 0 else "NO"))
        return cases
    return _gen

for k in range(2, 22):
    PROBLEMS.append({
        "title": f"Divisible by {k}",
        "description": f"**Topic: Math**\n\nGiven an integer N, print \"YES\" if N is perfectly divisible by {k}, otherwise print \"NO\".",
        "difficulty": "easy",
        "rating": 800,
        "input_format": "A single integer N.",
        "output_format": "Print YES or NO.",
        "constraints": "-10^9 ≤ N ≤ 10^9",
        "time_limit_ms": 1000,
        "memory_limit_mb": 256,
        "gen": make_math_gen(k)
    })

# --- 2. Arrays Problems (20) ---
def make_array_gen(x):
    def _gen():
        random.seed(x * 100 + 1)
        cases = []
        cases.append((f"1\n{x}", "0"))
        cases.append((f"1\n{x+1}", str(x+1)))
        for _ in range(998):
            n = random.randint(1, 100)
            arr = [random.randint(-100, 100) for _ in range(n)]
            ans = sum(val for val in arr if val > x)
            cases.append((f"{n}\n{' '.join(map(str, arr))}", str(ans)))
        return cases
    return _gen

for x in range(-10, 10):
    PROBLEMS.append({
        "title": f"Sum Elements Greater Than {x}",
        "description": f"**Topic: Arrays**\n\nGiven an array of N integers, find the sum of all elements that are strictly greater than {x}.",
        "difficulty": "easy",
        "rating": 800,
        "input_format": "Line 1: integer N.\nLine 2: N space-separated integers.",
        "output_format": "An integer representing the sum.",
        "constraints": "1 ≤ N ≤ 1000, -100 ≤ arr[i] ≤ 100",
        "time_limit_ms": 1000,
        "memory_limit_mb": 256,
        "gen": make_array_gen(x)
    })

# --- 3. Strings Problems (20) ---
def make_string_gen(c):
    def _gen():
        random.seed(ord(c) * 100 + 2)
        cases = []
        cases.append((c, "1"))
        cases.append(("z" if c != 'z' else "a", "0"))
        for _ in range(998):
            n = random.randint(1, 1000)
            s = "".join(random.choices(string.ascii_lowercase, k=n))
            cases.append((s, str(s.count(c))))
        return cases
    return _gen

chars = "abcdefghijklmnopqrst"
for c in chars:
    PROBLEMS.append({
        "title": f"Count Occurrences of '{c}'",
        "description": f"**Topic: Strings**\n\nGiven a string S consisting of lowercase English letters, count how many times the character '{c}' appears in it.",
        "difficulty": "easy",
        "rating": 800,
        "input_format": "A single continuous string S.",
        "output_format": "An integer, the count of instances.",
        "constraints": "1 ≤ |S| ≤ 10^4",
        "time_limit_ms": 1000,
        "memory_limit_mb": 256,
        "gen": make_string_gen(c)
    })

# --- 4. Loops Problems (20) ---
def make_loop_gen(m):
    def _gen():
        random.seed(m * 100 + 3)
        cases = []
        cases.append(("1", str(m)))
        cases.append(("2", f"{m} {2*m}"))
        for _ in range(998):
            n = random.randint(1, 500)
            ans = " ".join(str(m * i) for i in range(1, n+1))
            cases.append((str(n), ans))
        return cases
    return _gen

for m in range(2, 22):
    PROBLEMS.append({
        "title": f"First N Multiples of {m}",
        "description": f"**Topic: Loops**\n\nGiven an integer N, print the first N positive multiples of {m}, separated by spaces.",
        "difficulty": "easy",
        "rating": 800,
        "input_format": "A single integer N.",
        "output_format": "Space-separated integers representing the multiples.",
        "constraints": "1 ≤ N ≤ 1000",
        "time_limit_ms": 1000,
        "memory_limit_mb": 256,
        "gen": make_loop_gen(m)
    })

# --- 5. Conditionals Problems (20) ---
def make_cond_gen(a, b):
    def _gen():
        random.seed(a * 100 + b)
        cases = []
        cases.append((str(a), "In Range"))
        cases.append((str(b), "In Range"))
        cases.append((str(a-1), "Out of Range"))
        cases.append((str(b+1), "Out of Range"))
        for _ in range(996):
            if random.random() < 0.5:
                n = random.randint(a, b)
            else:
                n = random.randint(a - 1000, b + 1000)
            cases.append((str(n), "In Range" if a <= n <= b else "Out of Range"))
        return cases
    return _gen

for i in range(20):
    start = i * 10
    end = start + 50
    PROBLEMS.append({
        "title": f"Between {start} and {end}",
        "description": f"**Topic: Conditionals**\n\nGiven an integer N, check if it falls within the inclusive range [{start}, {end}]. Print \"In Range\" if it does, otherwise \"Out of Range\".",
        "difficulty": "easy",
        "rating": 800,
        "input_format": "A single integer N.",
        "output_format": "Print \"In Range\" or \"Out of Range\"",
        "constraints": "-10^6 ≤ N ≤ 10^6",
        "time_limit_ms": 1000,
        "memory_limit_mb": 256,
        "gen": make_cond_gen(start, end)
    })

# ── Main ──────────────────────────────────────────────────────────

async def main():
    try:
        conn = await asyncpg.connect(db_url)
    except Exception as e:
        print(f"Failed to connect to database using DSN='{db_url}': {e}")
        print("Make sure you are running the script in the same env as DB, or update DATABASE_URL.")
        return

    print("Attempting to insert 100 problems and 100,000 test cases...")
    print("This will process entirely using asyncpg.executemany for high performance.")
    total_problems = 0
    total_cases = 0

    for idx, prob in enumerate(PROBLEMS, 1):
        prob_id = str(uuid.uuid4())
        await conn.execute(
            """INSERT INTO problems
               (id, title, description, difficulty, input_format, output_format,
                constraints, time_limit_ms, memory_limit_mb, is_active, created_at)
               VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,true,NOW())
               ON CONFLICT DO NOTHING""",
            uuid.UUID(prob_id), prob["title"], prob["description"], prob["difficulty"],
            prob["input_format"], prob["output_format"], prob["constraints"],
            prob["time_limit_ms"], prob["memory_limit_mb"]
        )
        
        cases = prob["gen"]()
        
        # Prepare batch insert
        test_case_records = []
        for c_idx, (inp, out) in enumerate(cases, 1):
            test_case_records.append((
                uuid.uuid4(), 
                uuid.UUID(prob_id), 
                inp, 
                out, 
                c_idx <= 3, # First 3 are marked as samples
                c_idx
            ))
            
        await conn.executemany(
            """INSERT INTO test_cases (id, problem_id, input, expected_output, is_sample, order_index)
               VALUES ($1,$2,$3,$4,$5,$6)""",
            test_case_records
        )
        
        total_problems += 1
        total_cases += len(cases)
        
        if idx % 10 == 0:
            print(f"[{idx}/100] Inserted up to '{prob['title']}'...")

    await conn.close()
    print(f"\n✅ Done! Successfully inserted {total_problems} problems and {total_cases} test cases.")

if __name__ == "__main__":
    asyncio.run(main())
