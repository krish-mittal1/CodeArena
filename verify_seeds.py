import asyncio
import asyncpg
import os

db_url = os.environ.get("DATABASE_URL", "postgresql://postgres:krishisunique@localhost:5432/codearena")

async def verify():
    print(f"Connecting to database at {db_url}...")
    try:
        conn = await asyncpg.connect(db_url)
    except Exception as e:
        print(f"Failed to connect: {e}")
        return

    # Check total problems (we just seeded 100)
    problems_count = await conn.fetchval("SELECT COUNT(*) FROM problems")
    print(f"\nTotal problems in database: {problems_count}")

    # Check test cases total
    tc_count = await conn.fetchval("SELECT COUNT(*) FROM test_cases")
    print(f"Total test cases in database: {tc_count}")

    # Get a sample problem we just generated, e.g., 'Divisible by 7'
    prob = await conn.fetchrow("SELECT id, title, description FROM problems WHERE title = 'Divisible by 7'")
    if prob:
        print(f"\n--- Found sample problem: '{prob['title']}' ---")
        print(f"Description:\n{prob['description']}")
        
        # Check its test cases
        ptc_count = await conn.fetchval("SELECT COUNT(*) FROM test_cases WHERE problem_id = $1", prob['id'])
        print(f"\nTest cases for '{prob['title']}': {ptc_count} (Expected: 1000)")
        
        # Look at the first 3 test cases
        print("\nSample test cases:")
        samples = await conn.fetch("SELECT input, expected_output FROM test_cases WHERE problem_id = $1 ORDER BY order_index ASC LIMIT 5", prob['id'])
        for i, s in enumerate(samples, 1):
            print(f"  Case {i}: Input: {s['input'].strip()} => Output: {s['expected_output'].strip()}")
    else:
        print("\nCould not find 'Divisible by 7' problem. Did seeding fail?")

    await conn.close()
    print("\nVerification complete.")

if __name__ == "__main__":
    asyncio.run(verify())
