"""
OTP auth routes — request and verify email OTP.
"""

import logging

from fastapi import APIRouter, Depends, Request

from backend.db.session import get_db, AsyncSession
from backend.schemas.otp import OTPRequest, OTPVerify, OTPResponse
from backend.schemas.user import TokenResponse
from backend.services import otp_service
from backend.dependencies import get_client_ip, get_redis

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/request-otp", response_model=OTPResponse)
async def request_otp(data: OTPRequest, request: Request):
    """
    Send a 6-digit OTP to the given email.
    Rate limited: 3/email/hour, 5/IP/hour.
    Always returns success to prevent user enumeration.
    """
    ip = get_client_ip(request)

    try:
        debug_otp = await otp_service.request_otp(data.email, ip)
    except Exception as e:
        # Re-raise structured exceptions (rate limit, disposable email)
        from backend.core.exceptions import AppException
        if isinstance(e, AppException):
            raise
        # Swallow other errors to prevent user enumeration
        logger.error(f"OTP request failed for {data.email}: {e}", exc_info=True)
        debug_otp = None

    return OTPResponse(
        message="If this email is valid, you will receive a verification code shortly.",
        debug_otp=debug_otp,
    )


@router.post("/verify-otp", response_model=TokenResponse)
async def verify_otp(
    data: OTPVerify,
    request: Request,
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
):
    """
    Verify OTP and return JWT tokens.
    Auto-creates user if email not registered.
    Rate limited to prevent brute-force attempts.
    """
    ip = get_client_ip(request)
    user_agent = request.headers.get("user-agent", "unknown")

    from backend.core.auth_rate_limit import ensure_login_allowed, record_login_failure, clear_login_failures
    verify_key = f"otp_verify:{data.email}"
    await ensure_login_allowed(verify_key, ip, redis=redis)

    try:
        result = await otp_service.verify_otp(
            email=data.email,
            otp=data.otp,
            ip=ip,
            user_agent=user_agent,
            db=db,
        )
        await clear_login_failures(verify_key, ip, redis=redis)
        return result
    except Exception:
        await record_login_failure(verify_key, ip, redis=redis)
        raise


@router.post("/verify-otp-only", response_model=OTPResponse)
async def verify_otp_only(
    data: OTPVerify,
    request: Request,
    redis=Depends(get_redis),
):
    """
    Verify OTP only — does NOT create a user or issue tokens.
    Used for registration email verification.
    Rate limited to prevent brute-force attempts.
    """
    ip = get_client_ip(request)

    from backend.core.auth_rate_limit import ensure_login_allowed, record_login_failure, clear_login_failures
    verify_key = f"otp_verify_only:{data.email}"
    await ensure_login_allowed(verify_key, ip, redis=redis)

    try:
        await otp_service.verify_otp_only(email=data.email, otp=data.otp)
        await clear_login_failures(verify_key, ip, redis=redis)
        return OTPResponse(message="Email verified successfully.")
    except Exception:
        await record_login_failure(verify_key, ip, redis=redis)
        raise
