"""
OTP authentication service.

- Dedicated Redis connection (independent of main app Redis)
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
from datetime import datetime, timezone

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

# ── Redis keys ────────────────────────────────────────────────

_KEY_OTP = "otp:code:{email}"
_KEY_ATTEMPTS = "otp:attempts:{email}"
_KEY_RATE_EMAIL = "otp:rate:email:{email}"
_KEY_RATE_IP = "otp:rate:ip:{ip}"

# ── Dedicated Redis connection for OTP ────────────────────────

_otp_redis: aioredis.Redis | None = None


async def _get_otp_redis() -> aioredis.Redis:
    """Lazy-init a dedicated Redis client for OTP storage."""
    global _otp_redis
    if _otp_redis is None:
        _otp_redis = aioredis.from_url(
            settings.redis_url,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
        )
        await _otp_redis.ping()
        logger.info("OTP Redis connection established")
    return _otp_redis


# ── Disposable email blocklist ────────────────────────────────

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


# ── OTP generation & hashing ─────────────────────────────────

def _generate_otp() -> str:
    return str(secrets.randbelow(900000) + 100000)


def _hash_otp(otp: str) -> str:
    return hashlib.sha256(otp.encode("utf-8")).hexdigest()


def _compare_otp(plain: str, hashed: str) -> bool:
    return hmac.compare_digest(_hash_otp(plain), hashed)


# ── Rate limiting ─────────────────────────────────────────────

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


async def _increment_rate(r: aioredis.Redis, email: str, ip: str) -> None:
    pipe = r.pipeline()
    email_key = _KEY_RATE_EMAIL.format(email=email.lower())
    ip_key = _KEY_RATE_IP.format(ip=ip)

    pipe.incr(email_key)
    pipe.expire(email_key, 3600, nx=True)
    pipe.incr(ip_key)
    pipe.expire(ip_key, 3600, nx=True)
    await pipe.execute()


# ── Email sending via Resend ──────────────────────────────────

async def _send_otp_email(email: str, otp: str) -> None:
    if not settings.resend_api_key:
        logger.warning("RESEND_API_KEY not set — OTP not emailed, logging instead")
        logger.info(f"[DEV] OTP for {email}: {otp}")
        return

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
    except Exception as e:
        logger.error(f"Failed to send OTP email to {email}: {e}", exc_info=True)
        raise


# ── Public API ────────────────────────────────────────────────

async def request_otp(email: str, ip: str) -> None:
    """Generate, store, rate-limit, and send an OTP."""
    email = email.lower().strip()

    if _is_disposable(email):
        raise DisposableEmailBlocked()

    r = await _get_otp_redis()

    await _check_rate_limits(r, email, ip)

    otp = _generate_otp()
    hashed = _hash_otp(otp)

    otp_key = _KEY_OTP.format(email=email)
    attempts_key = _KEY_ATTEMPTS.format(email=email)

    pipe = r.pipeline()
    pipe.set(otp_key, hashed, ex=settings.otp_expire_seconds)
    pipe.delete(attempts_key)  # Reset attempts on new OTP
    await pipe.execute()

    await _increment_rate(r, email, ip)
    await _send_otp_email(email, otp)


async def verify_otp_only(email: str, otp: str) -> bool:
    """Verify OTP without creating a user — just check the code is valid.
    Used for registration email verification.
    Returns True if valid, raises otherwise.
    """
    email = email.lower().strip()

    r = await _get_otp_redis()
    otp_key = _KEY_OTP.format(email=email)
    attempts_key = _KEY_ATTEMPTS.format(email=email)

    # Check attempt count
    attempts = await r.get(attempts_key)
    if attempts and int(attempts) >= settings.otp_max_attempts:
        await r.delete(otp_key)
        raise OTPMaxAttemptsExceeded()

    # Retrieve stored hash
    stored_hash = await r.get(otp_key)
    if not stored_hash:
        raise OTPInvalid()

    # Constant-time comparison
    if not _compare_otp(otp, stored_hash):
        pipe = r.pipeline()
        pipe.incr(attempts_key)
        pipe.expire(attempts_key, settings.otp_expire_seconds, nx=True)
        await pipe.execute()
        raise OTPInvalid()

    # OTP valid — delete it (single-use)
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
    """Verify OTP, find-or-create user, issue JWT tokens."""
    email = email.lower().strip()

    r = await _get_otp_redis()
    otp_key = _KEY_OTP.format(email=email)
    attempts_key = _KEY_ATTEMPTS.format(email=email)

    # ── Check attempt count ───────────────────────────────
    attempts = await r.get(attempts_key)
    if attempts and int(attempts) >= settings.otp_max_attempts:
        await r.delete(otp_key)  # Invalidate OTP after too many failures
        raise OTPMaxAttemptsExceeded()

    # ── Retrieve stored hash ──────────────────────────────
    stored_hash = await r.get(otp_key)
    if not stored_hash:
        raise OTPInvalid()

    # ── Constant-time comparison ──────────────────────────
    if not _compare_otp(otp, stored_hash):
        pipe = r.pipeline()
        pipe.incr(attempts_key)
        pipe.expire(attempts_key, settings.otp_expire_seconds, nx=True)
        await pipe.execute()
        raise OTPInvalid()

    # ── OTP valid — delete it (single-use) ────────────────
    pipe = r.pipeline()
    pipe.delete(otp_key)
    pipe.delete(attempts_key)
    await pipe.execute()

    # ── Find or create user ───────────────────────────────
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if user is None:
        username = f"user_{uuid.uuid4().hex[:8]}"
        user = User(
            username=username,
            email=email,
            password_hash="__otp_only__",  # No password — OTP-only account
            elo=ELO_DEFAULT,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        logger.info(f"OTP: created new user {user.id} ({email})")

    # ── Issue tokens ──────────────────────────────────────
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
