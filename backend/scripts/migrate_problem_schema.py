import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

from backend.config import settings

DATABASE_URL = settings.database_url

async def upgrade_db():
    engine = create_async_engine(DATABASE_URL)
    async with engine.begin() as conn:
        try:
            await conn.execute(
                text("ALTER TABLE problems ADD COLUMN method_name VARCHAR(200);")
            )
            print("Added method_name")
        except Exception as e:
            print(e)
            
        try:
            await conn.execute(
                text("ALTER TABLE problems ADD COLUMN parameters JSONB;")
            )
            print("Added parameters")
        except Exception as e:
            print(e)
            
        try:
            await conn.execute(
                text("ALTER TABLE problems ADD COLUMN return_type VARCHAR(100);")
            )
            print("Added return_type")
        except Exception as e:
            print(e)

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(upgrade_db())
