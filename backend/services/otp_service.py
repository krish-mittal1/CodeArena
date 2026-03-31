"""
OTP authentication service.

- Redis-backed OTP storage in normal environments
- In-memory OTP fallback for development when Redis is disabled/unavailable
- Rate limiting per email and IP
- Brute-force protection with attempt tracking
- Disposable email blocking
- Constant-time OTP comparison
- Resend integration for HTML email delivery
"""

from __future__ import annotations

import hashlib
import hmac
import logging
import secrets
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

import redis.asyncio as aioredis
import resend
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.config import settings
from backend.core.constants import ELO_DEFAULT
from backend.core.exceptions import (
    DisposableEmailBlocked,
    OTPInvalid,
    OTPMaxAttemptsExceeded,
    OTPRateLimited,
)
from backend.core.security import create_access_token, create_refresh_token
from backend.models.user import User
from backend.schemas.user import TokenResponse

logger = logging.getLogger(__name__)

_KEY_OTP = "otp:code:{email}"
_KEY_ATTEMPTS = "otp:attempts:{email}"
_KEY_RATE_EMAIL = "otp:rate:email:{email}"
_KEY_RATE_IP = "otp:rate:ip:{ip}"

_otp_redis: Optional[aioredis.Redis] = None

_dev_otp_store: dict[str, tuple[str, datetime]] = {}
_dev_attempt_store: dict[str, tuple[int, datetime]] = {}
_dev_rate_email_store: dict[str, tuple[int, datetime]] = {}
_dev_rate_ip_store: dict[str, tuple[int, datetime]] = {}


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _get_store_value(store: dict[str, tuple[object, datetime]], key: str):
    entry = store.get(key)
    if entry is None:
        return None

    value, expires_at = entry
    if expires_at <= _now():
        store.pop(key, None)
        return None

    return value


def _set_store_value(
    store: dict[str, tuple[object, datetime]],
    key: str,
    value: object,
    expires_in_seconds: int,
) -> None:
    store[key] = (value, _now() + timedelta(seconds=expires_in_seconds))


def _delete_store_value(store: dict[str, tuple[object, datetime]], key: str) -> None:
    store.pop(key, None)


def _increment_store_value(
    store: dict[str, tuple[int, datetime]],
    key: str,
    expires_in_seconds: int,
) -> int:
    current = _get_store_value(store, key)
    next_value = int(current or 0) + 1
    _set_store_value(store, key, next_value, expires_in_seconds)
    return next_value


async def _get_otp_redis() -> Optional[aioredis.Redis]:
    """Lazy-init a dedicated Redis client for OTP storage."""
    global _otp_redis

    if not settings.redis_enabled:
        return None

    if _otp_redis is None:
        try:
            _otp_redis = aioredis.from_url(
                settings.redis_url,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
            )
            await _otp_redis.ping()
            logger.info("OTP Redis connection established")
        except Exception:
            _otp_redis = None
            if settings.is_development:
                logger.warning(
                    "OTP Redis unavailable in development; using in-memory OTP storage",
                    exc_info=True,
                )
                return None
            raise

    return _otp_redis


DISPOSABLE_DOMAINS = frozenset({
    "mailinator.com", "guerrillamail.com", "tempmail.com", "throwaway.email",
    "temp-mail.org", "fakeinbox.com", "sharklasers.com", "guerrillamailblock.com",
    "grr.la", "dispostable.com", "yopmail.com", "trashmail.com", "maildrop.cc",
    "10minutemail.com", "minutemail.com", "tempr.email", "discard.email",
    "mailnesia.com", "getnada.com", "emailondeck.com", "tempail.com",
    "burnermail.io", "inboxkitten.com", "33mail.com", "maildrop.cc",
    "mohmal.com", "tmail.ws", "harakirimail.com", "crazymailing.com",
    "mytemp.email", "tempmailo.com", "tempmailaddress.com", "tmpmail.net",
    "tmpmail.org", "bupmail.com", "mailsac.com", "mailcatch.com",
    "jetable.org", "trash-mail.com", "getairmail.com", "meltmail.com",
    "spamgourmet.com", "mailexpire.com", "incognitomail.org", "anonbox.net",
    "mytrashmail.com", "mailforspam.com", "safetymail.info", "filzmail.com",
    "trashmail.me", "trashmail.net", "thankyou2010.com",
})


def _is_disposable(email: str) -> bool:
    domain = email.rsplit("@", 1)[-1].lower()
    return domain in DISPOSABLE_DOMAINS


def _generate_otp() -> str:
    return str(secrets.randbelow(900000) + 100000)


def _hash_otp(otp: str) -> str:
    return hashlib.sha256(otp.encode("utf-8")).hexdigest()


def _compare_otp(plain: str, hashed: str) -> bool:
    return hmac.compare_digest(_hash_otp(plain), hashed)


async def _check_rate_limits(r: aioredis.Redis, email: str, ip: str) -> None:
    pipe = r.pipeline()
    email_key = _KEY_RATE_EMAIL.format(email=email.lower())
    ip_key = _KEY_RATE_IP.format(ip=ip)

    pipe.get(email_key)
    pipe.get(ip_key)
    email_count, ip_count = await pipe.execute()

    if email_count and int(email_count) >= settings.otp_rate_limit_email:
        logger.warning(f"OTP rate limit hit for email={email}")
        raise OTPRateLimited()

    if ip_count and int(ip_count) >= settings.otp_rate_limit_ip:
        logger.warning(f"OTP rate limit hit for ip={ip}")
        raise OTPRateLimited()


def _check_rate_limits_dev(email: str, ip: str) -> None:
    email_count = _get_store_value(_dev_rate_email_store, email.lower())
    ip_count = _get_store_value(_dev_rate_ip_store, ip)

    if email_count and int(email_count) >= settings.otp_rate_limit_email:
        logger.warning(f"OTP rate limit hit for email={email}")
        raise OTPRateLimited()

    if ip_count and int(ip_count) >= settings.otp_rate_limit_ip:
        logger.warning(f"OTP rate limit hit for ip={ip}")
        raise OTPRateLimited()


async def _increment_rate(r: aioredis.Redis, email: str, ip: str) -> None:
    pipe = r.pipeline()
    email_key = _KEY_RATE_EMAIL.format(email=email.lower())
    ip_key = _KEY_RATE_IP.format(ip=ip)

    pipe.incr(email_key)
    pipe.expire(email_key, 3600, nx=True)
    pipe.incr(ip_key)
    pipe.expire(ip_key, 3600, nx=True)
    await pipe.execute()


def _increment_rate_dev(email: str, ip: str) -> None:
    _increment_store_value(_dev_rate_email_store, email.lower(), 3600)
    _increment_store_value(_dev_rate_ip_store, ip, 3600)


async def _send_otp_email(email: str, otp: str) -> bool:
    if not settings.resend_api_key:
        logger.warning("RESEND_API_KEY not set; OTP not emailed, logging instead")
        logger.info(f"[DEV] OTP for {email}: {otp}")
        return False

    resend.api_key = settings.resend_api_key

    html = f"""
    <div style="font-family: 'Segoe UI', Arial, sans-serif; max-width: 480px; margin: 0 auto;
                padding: 32px; background: #0f172a; border-radius: 12px; color: #e2e8f0;">
        <h2 style="color: #38bdf8; margin: 0 0 8px 0; font-size: 22px;">CodeArena</h2>
        <p style="color: #94a3b8; margin: 0 0 24px 0; font-size: 14px;">Your login verification code</p>
        <div style="background: #1e293b; border-radius: 8px; padding: 24px; text-align: center;
                    border: 1px solid #334155;">
            <span style="font-size: 36px; font-weight: 700; letter-spacing: 8px; color: #f1f5f9;
                         font-family: 'Courier New', monospace;">{otp}</span>
        </div>
        <p style="color: #64748b; font-size: 13px; margin: 20px 0 0 0; line-height: 1.5;">
            This code expires in <strong style="color: #94a3b8;">5 minutes</strong>.
            If you didn't request this, ignore this email.
        </p>
    </div>
    """

    try:
        resend.Emails.send({
            "from": settings.otp_from_email,
            "to": [email],
            "subject": "Your CodeArena login code",
            "html": html,
        })
        logger.info(f"OTP email sent to {email}")
        return True
    except Exception as exc:
        if settings.is_development:
            logger.warning(
                f"Failed to send OTP email to {email}; using development fallback: {exc}",
                exc_info=True,
            )
            logger.info(f"[DEV] OTP for {email}: {otp}")
            return False
        logger.error(f"Failed to send OTP email to {email}: {exc}", exc_info=True)
        raise


async def request_otp(email: str, ip: str) -> Optional[str]:
    """Generate, store, rate-limit, and send an OTP."""
    email = email.lower().strip()

    if _is_disposable(email):
        raise DisposableEmailBlocked()

    r = await _get_otp_redis()
    otp = _generate_otp()
    hashed = _hash_otp(otp)

    if r is None:
        _check_rate_limits_dev(email, ip)
        _set_store_value(_dev_otp_store, email, hashed, settings.otp_expire_seconds)
        _delete_store_value(_dev_attempt_store, email)
        _increment_rate_dev(email, ip)
    else:
        await _check_rate_limits(r, email, ip)

        otp_key = _KEY_OTP.format(email=email)
        attempts_key = _KEY_ATTEMPTS.format(email=email)

        pipe = r.pipeline()
        pipe.set(otp_key, hashed, ex=settings.otp_expire_seconds)
        pipe.delete(attempts_key)
        await pipe.execute()

        await _increment_rate(r, email, ip)

    email_sent = await _send_otp_email(email, otp)
    return otp if settings.is_development and not email_sent else None


async def verify_otp_only(email: str, otp: str) -> bool:
    """
    Verify OTP without creating a user.
    Used for registration email verification.
    """
    email = email.lower().strip()

    r = await _get_otp_redis()
    if r is None:
        attempts = _get_store_value(_dev_attempt_store, email)
        if attempts and int(attempts) >= settings.otp_max_attempts:
            _delete_store_value(_dev_otp_store, email)
            raise OTPMaxAttemptsExceeded()

        stored_hash = _get_store_value(_dev_otp_store, email)
        if not stored_hash:
            raise OTPInvalid()

        if not _compare_otp(otp, stored_hash):
            _increment_store_value(_dev_attempt_store, email, settings.otp_expire_seconds)
            raise OTPInvalid()

        _delete_store_value(_dev_otp_store, email)
        _delete_store_value(_dev_attempt_store, email)
    else:
        otp_key = _KEY_OTP.format(email=email)
        attempts_key = _KEY_ATTEMPTS.format(email=email)

        attempts = await r.get(attempts_key)
        if attempts and int(attempts) >= settings.otp_max_attempts:
            await r.delete(otp_key)
            raise OTPMaxAttemptsExceeded()

        stored_hash = await r.get(otp_key)
        if not stored_hash:
            raise OTPInvalid()

        if not _compare_otp(otp, stored_hash):
            pipe = r.pipeline()
            pipe.incr(attempts_key)
            pipe.expire(attempts_key, settings.otp_expire_seconds, nx=True)
            await pipe.execute()
            raise OTPInvalid()

        pipe = r.pipeline()
        pipe.delete(otp_key)
        pipe.delete(attempts_key)
        await pipe.execute()

    logger.info(f"OTP: email verified (check only) for {email}")
    return True


async def verify_otp(
    email: str,
    otp: str,
    ip: str,
    user_agent: str,
    db: AsyncSession,
) -> TokenResponse:
    """Verify OTP, find-or-create user, and issue JWT tokens."""
    email = email.lower().strip()

    r = await _get_otp_redis()
    if r is None:
        attempts = _get_store_value(_dev_attempt_store, email)
        if attempts and int(attempts) >= settings.otp_max_attempts:
            _delete_store_value(_dev_otp_store, email)
            raise OTPMaxAttemptsExceeded()

        stored_hash = _get_store_value(_dev_otp_store, email)
        if not stored_hash:
            raise OTPInvalid()

        if not _compare_otp(otp, stored_hash):
            _increment_store_value(_dev_attempt_store, email, settings.otp_expire_seconds)
            raise OTPInvalid()

        _delete_store_value(_dev_otp_store, email)
        _delete_store_value(_dev_attempt_store, email)
    else:
        otp_key = _KEY_OTP.format(email=email)
        attempts_key = _KEY_ATTEMPTS.format(email=email)

        attempts = await r.get(attempts_key)
        if attempts and int(attempts) >= settings.otp_max_attempts:
            await r.delete(otp_key)
            raise OTPMaxAttemptsExceeded()

        stored_hash = await r.get(otp_key)
        if not stored_hash:
            raise OTPInvalid()

        if not _compare_otp(otp, stored_hash):
            pipe = r.pipeline()
            pipe.incr(attempts_key)
            pipe.expire(attempts_key, settings.otp_expire_seconds, nx=True)
            await pipe.execute()
            raise OTPInvalid()

        pipe = r.pipeline()
        pipe.delete(otp_key)
        pipe.delete(attempts_key)
        await pipe.execute()

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if user is None:
        username = f"user_{uuid.uuid4().hex[:8]}"
        user = User(
            username=username,
            email=email,
            password_hash="__otp_only__",
            elo=ELO_DEFAULT,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        logger.info(f"OTP: created new user {user.id} ({email})")

    subject = str(user.id)
    tokens = TokenResponse(
        access_token=create_access_token(subject, extra={"username": user.username}),
        refresh_token=create_refresh_token(subject),
    )

    logger.info(
        f"OTP: verified login for {user.id} ({email}) "
        f"ip={ip} ua={user_agent[:80]}"
    )

    return tokens
