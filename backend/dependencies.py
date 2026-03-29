"""
FastAPI dependency injection — DB sessions, Redis, current user.
"""

import uuid
import asyncio
import time
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import redis.asyncio as aioredis

from backend.config import settings
from backend.db.session import get_db, AsyncSession
from backend.core.security import decode_token
from backend.core.exceptions import InvalidCredentials
from backend.models.user import User
from backend.services.auth_service import get_user_by_id

security_scheme = HTTPBearer()

# ── Redis Dependency ──────────────────────────────────────────

_redis: Optional[aioredis.Redis] = None
_redis_initialized: bool = False
_redis_retry_after: float = 0.0
_redis_forced_disabled: bool = False


def set_redis_forced_disabled(disabled: bool) -> None:
    """
    Force Redis dependency to return None for process lifetime (or until reset).

    Used when startup falls back to dev-mode matchmaking so request-time Redis
    reconnection cannot switch the app into a mixed mode.
    """
    global _redis_forced_disabled
    _redis_forced_disabled = disabled


async def get_redis() -> Optional[aioredis.Redis]:
    """
    Get the shared Redis connection. Returns None if Redis is disabled.
    
    PRODUCTION: Ensures connection is tested before returning to prevent
    deadlocks from lazy connection initialization.
    """
    global _redis, _redis_initialized, _redis_retry_after
    
    if _redis_forced_disabled or not settings.redis_enabled:
        return None

    # After a failed attempt, back off briefly instead of reconnecting on every request.
    if _redis is None and _redis_retry_after and time.monotonic() < _redis_retry_after:
        return None
    
    if _redis is None:
        try:
            _redis = aioredis.from_url(
                settings.redis_url,
                decode_responses=False,
                socket_connect_timeout=5,
                socket_timeout=5,
                socket_keepalive=True,
                retry_on_timeout=True,
                health_check_interval=30,
            )
            # Test connection immediately (fail fast)
            await asyncio.wait_for(_redis.ping(), timeout=3)
            _redis_initialized = True
            _redis_retry_after = 0.0
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Redis connection failed: {e}")
            _redis = None
            _redis_initialized = False
            _redis_retry_after = time.monotonic() + 15
            return None
    
    # Verify connection is still alive
    if _redis_initialized:
        try:
            await asyncio.wait_for(_redis.ping(), timeout=1)
        except Exception:
            # Connection lost, reset
            try:
                await _redis.close()
            except Exception:
                pass
            _redis = None
            _redis_initialized = False
            _redis_retry_after = time.monotonic() + 15
            return None
    
    return _redis


async def close_redis():
    """Close Redis connection on shutdown."""
    global _redis, _redis_initialized, _redis_retry_after
    if _redis:
        try:
            await asyncio.wait_for(_redis.close(), timeout=5)
        except Exception:
            pass
        _redis = None
        _redis_initialized = False
    _redis_retry_after = 0.0


# ── Auth Dependencies ─────────────────────────────────────────

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Extract and validate the current user from JWT token."""
    token = credentials.credentials
    payload = decode_token(token)

    if payload.get("type") != "access":
        raise InvalidCredentials()

    user_id = uuid.UUID(payload["sub"])
    user = await get_user_by_id(db, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user
