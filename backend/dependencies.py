"""
FastAPI dependency injection — DB sessions, Redis, current user.
"""

import uuid
import asyncio
import time
from typing import Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import redis.asyncio as aioredis

from backend.config import settings
from backend.db.session import get_db, AsyncSession
from backend.core.security import decode_token
from backend.core.exceptions import InvalidCredentials
from backend.models.user import User
from backend.services.auth_service import get_user_by_id

security_scheme = HTTPBearer()
optional_security_scheme = HTTPBearer(auto_error=False)

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

    PRODUCTION: We only ping on the very first connection to fail fast.
    Subsequent calls return the cached client directly — the pool's built-in
    `health_check_interval=30` handles reconnect detection without adding a
    round-trip to every HTTP request or WebSocket connection.
    """
    global _redis, _redis_initialized, _redis_retry_after

    if _redis_forced_disabled or not settings.redis_enabled:
        return None

    # After a failed attempt, back off before retrying to avoid hammering Redis.
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
                # Pool-level health check: automatically detects dead connections
                # every 30s without any per-request overhead.
                health_check_interval=30,
            )
            # Ping ONCE on first init to verify the address is reachable.
            await asyncio.wait_for(_redis.ping(), timeout=3)
            _redis_initialized = True
            _redis_retry_after = 0.0
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Redis connection failed: {e}")
            _redis = None
            _redis_initialized = False
            # Back off 15 s before attempting to reconnect.
            _redis_retry_after = time.monotonic() + 15
            return None

    # NOTE: No per-request ping here — it would add ~1 ms of latency to every
    # request and is redundant with health_check_interval=30 on the pool.
    # If a command fails due to a broken connection, redis-py raises an error
    # which the caller handles; the next get_redis() call will recreate the
    # client automatically (via the _redis is None branch above).
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


async def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(optional_security_scheme),
    db: AsyncSession = Depends(get_db),
) -> Optional[User]:
    """Best-effort user extraction for endpoints that can work anonymously."""
    if credentials is None:
        return None

    token = credentials.credentials

    try:
        payload = decode_token(token)
    except Exception:
        return None

    if payload.get("type") != "access":
        return None

    try:
        user_id = uuid.UUID(payload["sub"])
    except Exception:
        return None

    return await get_user_by_id(db, user_id)


async def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """Enforce admin access control."""
    from backend.core.exceptions import AdminAccessRequired
    if not current_user.is_admin:
        raise AdminAccessRequired()
    return current_user


def _parse_proxy_networks(entries: list[str]):
    """Parse trusted_proxies into ipaddress networks (cached per call list)."""
    import ipaddress

    networks = []
    for entry in entries:
        try:
            networks.append(ipaddress.ip_network(entry, strict=False))
        except ValueError:
            continue
    return networks


def _ip_in_trusted(ip_str: str, networks) -> bool:
    import ipaddress

    try:
        ip = ipaddress.ip_address(ip_str)
    except ValueError:
        return False
    return any(ip in net for net in networks)


def get_client_ip(request: Request) -> str:
    """
    Extract the client IP for rate limiting (OTP / auth / room codes).

    By default ``settings.trust_forwarded_headers`` is False: X-Forwarded-For
    is ignored and ``request.client.host`` is used. Enable trust only behind a
    reverse proxy (Azure / Pangolin / nginx).

    When trust is True and ``trusted_proxies`` is set, XFF is honoured only if
    the immediate TCP peer is in that set; the client is the rightmost hop that
    is not trusted. When trust is True but ``trusted_proxies`` is empty, the
    leftmost XFF hop is used — the proxy must strip client-supplied XFF first.
    """
    peer = request.client.host if request.client else None

    if not settings.trust_forwarded_headers:
        return peer or "unknown"

    forwarded = request.headers.get("x-forwarded-for")
    if not forwarded:
        return peer or "unknown"

    hops = [h.strip() for h in forwarded.split(",") if h.strip()]
    if not hops:
        return peer or "unknown"

    trusted = _parse_proxy_networks(settings.trusted_proxies)
    if trusted:
        if not peer or not _ip_in_trusted(peer, trusted):
            # Peer is not a trusted proxy — ignore spoofable XFF.
            return peer or "unknown"
        for hop in reversed(hops):
            if not _ip_in_trusted(hop, trusted):
                return hop
        return hops[0]

    # Trusted-proxy list empty: leftmost hop (proxy must strip inbound XFF).
    return hops[0]
