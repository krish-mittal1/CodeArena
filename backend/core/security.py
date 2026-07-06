"""
JWT token management and password hashing utilities.
"""

import uuid
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
import bcrypt

from backend.config import settings
from backend.core.exceptions import InvalidCredentials, TokenExpired

_used_refresh_tokens: dict[str, float] = {}


# ── Password ──────────────────────────────────────────────────

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    if not hashed or not hashed.startswith("$2"):
        return False
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except (ValueError, TypeError):
        return False


# ── JWT ───────────────────────────────────────────────────────

from typing import Optional

def create_access_token(subject: str, extra: Optional[dict] = None) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.jwt_access_token_expire_minutes
    )
    payload = {"sub": subject, "exp": expire, "type": "access"}
    if extra:
        payload.update(extra)
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_refresh_token(subject: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.jwt_refresh_token_expire_minutes
    )
    payload = {"sub": subject, "exp": expire, "type": "refresh", "jti": uuid.uuid4().hex}
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def consume_refresh_token(token: str) -> dict:
    """Decode a refresh token and mark it as used. Raises if already used (replay)."""
    import time
    _prune_used_tokens()
    payload = decode_token(token)
    if payload.get("type") != "refresh":
        raise InvalidCredentials()
    jti = payload.get("jti")
    if jti:
        if jti in _used_refresh_tokens:
            raise InvalidCredentials()
        _used_refresh_tokens[jti] = time.monotonic()
    return payload


def _prune_used_tokens() -> None:
    """Remove entries older than the refresh token lifetime to prevent unbounded growth."""
    import time
    cutoff = time.monotonic() - (settings.jwt_refresh_token_expire_minutes * 60)
    stale = [k for k, v in _used_refresh_tokens.items() if v < cutoff]
    for k in stale:
        del _used_refresh_tokens[k]


def decode_token(token: str) -> dict:
    """Decode and validate a JWT token. Raises on invalid/expired tokens."""
    try:
        payload = jwt.decode(
            token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
        )
        if payload.get("sub") is None:
            raise InvalidCredentials()
        return payload
    except JWTError as e:
        if "expired" in str(e).lower():
            raise TokenExpired()
        raise InvalidCredentials()
