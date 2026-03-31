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

import argparse
import asyncio
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.session import AsyncSessionLocal
from backend.models.user import User
from backend.services.bot_service import BOT_PROFILES

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def get_or_create_bots(db: AsyncSession, reset: bool = False):
    """Create or update bot users with stable profile identities."""

    if reset:
        result = await db.execute(select(User).where(User.is_bot == True))
        bots_to_delete = result.scalars().all()
        for bot in bots_to_delete:
            await db.delete(bot)
        await db.commit()
        logger.info(f"Deleted {len(bots_to_delete)} existing bot users")

    result = await db.execute(
        select(User)
        .where(User.is_bot == True)
        .order_by(User.created_at.asc(), User.id.asc())
    )
    existing_bots = list(result.scalars().all())

    for index, profile in enumerate(BOT_PROFILES):
        if index < len(existing_bots):
            bot = existing_bots[index]
            changed = False

            if bot.username != profile.username:
                bot.username = profile.username
                changed = True
            expected_email = f"{profile.username.lower()}@bot.local"
            if bot.email != expected_email:
                bot.email = expected_email
                changed = True
            if bot.elo != profile.elo:
                bot.elo = profile.elo
                changed = True
            if not bot.is_bot:
                bot.is_bot = True
                changed = True
            if bot.password_hash != "":
                bot.password_hash = ""
                changed = True

            if changed:
                logger.info("Updated bot profile: %s (ELO=%s)", profile.username, profile.elo)
            else:
                logger.info("Bot %s already exists (ELO=%s)", profile.username, bot.elo)
            continue

        bot = User(
            username=profile.username,
            email=f"{profile.username.lower()}@bot.local",
            password_hash="",
            is_bot=True,
            elo=profile.elo,
            matches_played=0,
            matches_won=0,
        )
        db.add(bot)
        logger.info("Created bot: %s with ELO %s", profile.username, profile.elo)

    await db.commit()
    logger.info(f"Total of {len(BOT_PROFILES)} bots seeded successfully")


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
