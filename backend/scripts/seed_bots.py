"""
Seed bot users into the database.

Usage:
    python -m backend.scripts.seed_bots [--reset]

Examples:
    # Create/update bot users in database
    python -m backend.scripts.seed_bots

    # Reset bots (delete existing and recreate)
    python -m backend.scripts.seed_bots --reset
"""

import asyncio
import logging
import argparse

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.session import AsyncSessionLocal
from backend.models.user import User
from backend.services.bot_service import BOT_USERNAMES
from backend.core.constants import ELO_DEFAULT

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def get_or_create_bots(db: AsyncSession, reset: bool = False):
    """Create or update bot users with varying ELOs."""
    
    if reset:
        # Delete existing bots
        result = await db.execute(select(User).where(User.is_bot == True))
        bots_to_delete = result.scalars().all()
        for bot in bots_to_delete:
            await db.delete(bot)
        await db.commit()
        logger.info(f"Deleted {len(bots_to_delete)} existing bot users")
    
    # Create bots with varying ELOs for realistic matchmaking
    elo_values = [100, 200, 300, 400, 500, 600, 700, 800]
    
    for i, username in enumerate(BOT_USERNAMES):
        # Check if bot already exists
        result = await db.execute(
            select(User).where(User.username == username)
        )
        existing_bot = result.scalar_one_or_none()
        
        if existing_bot and not reset:
            logger.info(f"Bot {username} already exists (ELO={existing_bot.elo})")
            continue
        
        # Assign rotating ELO values
        elo = elo_values[i % len(elo_values)]
        
        bot = User(
            username=username,
            email=f"{username}@bot.local",
            password_hash="",  # Bots don't authenticate
            is_bot=True,
            elo=elo,
            matches_played=0,
            matches_won=0,
        )
        db.add(bot)
        logger.info(f"Created bot: {username} with ELO {elo}")
    
    await db.commit()
    logger.info(f"Total of {len(BOT_USERNAMES)} bots seeded successfully")


async def main():
    parser = argparse.ArgumentParser(description="Seed bot users")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Delete existing bots and recreate them"
    )
    args = parser.parse_args()
    
    async with AsyncSessionLocal() as db:
        await get_or_create_bots(db, reset=args.reset)
        logger.info("Bot seeding completed!")


if __name__ == "__main__":
    asyncio.run(main())
