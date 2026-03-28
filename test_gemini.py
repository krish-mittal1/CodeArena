import asyncio
from backend.services.ai_service import analyze_code
from backend.config import settings

async def main():
    res = await analyze_code(
        problem_title="Two Sum",
        problem_description="Find two numbers",
        constraints=None,
        language="python",
        code="print('hello')",
        verdict_status="wrong_answer"
    )
    print(res)

if __name__ == "__main__":
    asyncio.run(main())
