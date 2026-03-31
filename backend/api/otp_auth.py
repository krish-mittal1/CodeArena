"""
OTP auth routes — request and verify email OTP.
"""

import logging

from fastapi import APIRouter, Depends, Request, status
from fastapi import HTTPException

from backend.db.session import get_db, AsyncSession
from backend.schemas.otp import OTPRequest, OTPVerify, OTPResponse
from backend.schemas.user import TokenResponse
from backend.services import otp_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/request-otp", response_model=OTPResponse)
async def request_otp(data: OTPRequest, request: Request):
    """
    Send a 6-digit OTP to the given email.
    Rate limited: 1/email/5min and 2/IP/5min.
    Returns 503 when OTP infrastructure (Redis/Email provider) is unavailable.
    """
    ip = request.client.host if request.client else "unknown"

    try:
        await otp_service.request_otp(data.email, ip)
    except Exception as e:
        # Re-raise structured app exceptions (rate limit, disposable email, etc.)
        from backend.core.exceptions import AppException
        if isinstance(e, AppException):
            raise

        # Infra failure should not look like success to clients.
        logger.error(f"OTP infrastructure failure for {data.email}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="OTP service temporarily unavailable. Please try again shortly.",
        )

    return OTPResponse(message="If this email is valid, you will receive a verification code shortly.")


@router.post("/verify-otp", response_model=TokenResponse)
async def verify_otp(
    data: OTPVerify,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Verify OTP and return JWT tokens.
    Auto-creates user if email not registered.
    """
    ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")

    return await otp_service.verify_otp(
        email=data.email,
        otp=data.otp,
        ip=ip,
        user_agent=user_agent,
        db=db,
    )


@router.post("/verify-otp-only", response_model=OTPResponse)
async def verify_otp_only(data: OTPVerify):
    """
    Verify OTP only — does NOT create a user or issue tokens.
    Used for registration email verification.
    """
    await otp_service.verify_otp_only(email=data.email, otp=data.otp)
    return OTPResponse(message="Email verified successfully.")
