"""
Matchmaking worker — periodic queue processing and expired match scanning.
Also handles bot auto-submissions for active matches.
Run separately: python -m workers.matchmaking_worker
"""

import json
import asyncio
import logging

import redis.asyncio as aioredis

from backend.config import settings
from backend.db.session import AsyncSessionLocal
from backend.core.constants import WSEvent, RedisKey
from backend.services import matchmaking_service, match_service, bot_submission_service

logger = logging.getLogger(__name__)


async def run_worker():
    """Main matchmaking worker loop."""
    redis = aioredis.from_url(settings.redis_url, decode_responses=False)
    poll_interval = settings.matchmaking_poll_interval_ms / 1000.0

    logger.info("Matchmaking worker started")

    while True:
        try:
            async with AsyncSessionLocal() as db:
                # Process matchmaking queue
                new_matches = await matchmaking_service.process_queue(redis, db)

                # Broadcast match_found events for newly created matches
                for match_id in new_matches:
                    match = await match_service.get_match(db, match_id)
                    if match:
                        await redis.publish(
                            RedisKey.ws_channel(str(match_id)),
                            json.dumps({
                                "event": WSEvent.MATCH_FOUND,
                                "data": {
                                    "match_id": str(match.id),
                                    "problem_id": str(match.problem_id),
                                    "problem_title": match.problem.title,
                                    "duration_seconds": match.duration_seconds,
                                    "player1": {
                                        "user_id": str(match.player1.id),
                                        "username": match.player1.username,
                                        "elo": match.player1.elo,
                                    },
                                    "player2": {
                                        "user_id": str(match.player2.id),
                                        "username": match.player2.username,
                                        "elo": match.player2.elo,
                                    },
                                },
                            })
                        )

                # Check for expired matches
                completed = await match_service.check_and_complete_expired_matches(db, redis)
                for match_id in completed:
                    logger.info(f"Match {match_id} expired and completed")
                
                # Process bot submissions for active matches
                bot_processed = await bot_submission_service.process_bot_submissions_for_active_matches(db, redis)
                if bot_processed > 0:
                    logger.debug(f"Processed bot submissions for {bot_processed} matches")

        except Exception as e:
            logger.error(f"Matchmaking worker error: {e}", exc_info=True)

        await asyncio.sleep(poll_interval)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run_worker())
