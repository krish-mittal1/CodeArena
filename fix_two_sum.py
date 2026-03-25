import asyncio
import asyncpg
import uuid
import random
import os

raw_url = os.environ.get("DATABASE_URL", "postgresql://postgres:krishisunique@api_postgres:5432/codexarena")
DB_DSN = raw_url.replace("postgresql+asyncpg://", "postgresql://")

def _two_sum_cases():
    random.seed(42)
    cases = []
    tests = [
        ([2,7,11,15],9), ([3,2,4],6), ([3,3],6),
        ([1,2,3,4,5],9), ([0,4,3,0],0), ([-1,-2,-3,-4,-5],-8),
        ([1000000000,-1000000000,0,1],1), ([-5,10,5,3,8],15),
        ([1,2],3), ([100,200,300],500),
    ]
    # Keep the manual tests (they are unique pairs)
    for arr,t in tests:
        # find pair
        for i in range(len(arr)):
            for j in range(i+1,len(arr)):
                if arr[i]+arr[j] == t:
                    inp = f"{len(arr)} {t}\n{' '.join(map(str,arr))}"
                    cases.append((inp, f"{i} {j}"))
                    break
            else:
                continue
            break
            
    # Random tests (Guarantee only ONE pair exists!)
    while len(cases) < 45:
        n = random.randint(2, 20)
        arr = [random.randint(-100, 100) for _ in range(n)]
        
        # Pick two distinct indices
        i, j = random.sample(range(n), 2)
        if i > j:
            i, j = j, i
            
        t = arr[i] + arr[j]
        
        # Check if exactly one pair exists
        count = 0
        for x in range(n):
            for y in range(x+1, n):
                if arr[x] + arr[y] == t:
                    count += 1
                    
        if count == 1:
            inp = f"{n} {t}\n{' '.join(map(str,arr))}"
            cases.append((inp, f"{i} {j}"))
            
    return cases


async def main():
    try:
        conn = await asyncpg.connect(DB_DSN)
    except Exception as e:
        print(f"Failed to connect to DB: {e}")
        return

    # Get Two Sum problem ID
    prob = await conn.fetchrow("SELECT id FROM problems WHERE title = 'Two Sum'")
    if not prob:
        print("Two Sum problem not found!")
        return
        
    prob_id = prob["id"]
    
    # Delete existing test cases and their associated submission histories
    print("Deleting old faulty test cases (and associated submissions) for Two Sum...")
    await conn.execute("DELETE FROM submission_results WHERE test_case_id IN (SELECT id FROM test_cases WHERE problem_id = $1)", prob_id)
    await conn.execute("DELETE FROM submissions WHERE problem_id = $1", prob_id)
    await conn.execute("DELETE FROM test_cases WHERE problem_id = $1", prob_id)
    
    # Generate exactly 45 completely valid test cases
    cases = _two_sum_cases()
    records = []
    for c_idx, (inp, out) in enumerate(cases, 1):
        records.append((
            uuid.uuid4(),
            prob_id,
            inp,
            out,
            c_idx <= 3, # first 3 are samples
            c_idx
        ))
        
    print(f"Inserting {len(records)} verified unique test cases...")
    await conn.executemany(
        """INSERT INTO test_cases (id, problem_id, input, expected_output, is_sample, order_index)
           VALUES ($1,$2,$3,$4,$5,$6)""",
        records
    )
    
    await conn.close()
    print("Two Sum problem fixed perfectly!")

if __name__ == "__main__":
    asyncio.run(main())
