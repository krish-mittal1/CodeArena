"""Public platform stats."""

from fastapi import APIRouter, Depends
from redis.asyncio import Redis
from typing import Optional

from backend.dependencies import get_redis
from backend.services.platform_stats_service import get_platform_stats

router = APIRouter(prefix="/stats", tags=["Stats"])


@router.get("/platform")
async def platform_stats(redis: Optional[Redis] = Depends(get_redis)):
    """Live queue depth, online users, and estimated wait for the dashboard."""
    return await get_platform_stats(redis)
