"""
Matchmaking worker — periodic queue processing and expired match scanning.
Run separately: python -m workers.matchmaking_worker
"""

import json
import asyncio
import logging

import redis.asyncio as aioredis

from backend.config import settings
from backend.db.session import AsyncSessionLocal
from backend.core.constants import WSEvent, RedisKey
from backend.services import matchmaking_service, match_service

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
                                "data": match_service.build_match_found_payload(match),
                            })
                        )

                # Check for expired matches and notify players
                completed_results = await match_service.check_and_complete_expired_matches(db, redis)
                for result_data in completed_results:
                    room_id = result_data["match_id"]
                    # Standalone worker: publish raw; API pods personalize via Redis listener
                    await redis.publish(
                        RedisKey.ws_channel(room_id),
                        json.dumps({
                            "event": WSEvent.MATCH_ENDED,
                            "data": result_data,
                        }),
                    )
                    logger.info(f"Match {room_id} expired and completed (timeout notified)")
                
        except Exception as e:
            logger.error(f"Matchmaking worker error: {e}", exc_info=True)

        await asyncio.sleep(poll_interval)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run_worker())
