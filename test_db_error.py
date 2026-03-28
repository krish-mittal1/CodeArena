from __future__ import annotations
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import select
from backend.config import settings
from backend.models.problem import Problem

async def main():
    engine = create_async_engine(settings.database_url)
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    
    async with async_session() as session:
        result = await session.execute(select(Problem).where(Problem.id == "7299ca25-f5de-414c-86f6-8c53d2b0c07c"))
        prob = result.scalars().first()
        if prob:
            print(f"FOUND PROBLEM: {prob.title}")
            print(f"Method Name: {prob.method_name}")
            print(f"Parameters: {prob.parameters}")
            print(f"Return: {prob.return_type}")
        else:
            print("NOT FOUND IN DATABASE!")

if __name__ == "__main__":
    asyncio.run(main())
