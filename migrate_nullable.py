import asyncio
import asyncpg

async def migrate():
    conn = await asyncpg.connect('postgresql://postgres:krishisunique@localhost:5432/codearena')
    await conn.execute('ALTER TABLE submissions ALTER COLUMN match_id DROP NOT NULL')
    await conn.close()
    print('OK: match_id is now nullable')

asyncio.run(migrate())
