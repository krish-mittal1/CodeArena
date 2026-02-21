"""
Auth service — registration, login, token management.
"""

import uuid
import secrets
import hashlib
from datetime import datetime, timezone, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import BackgroundTasks

from backend.core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from backend.core.exceptions import InvalidCredentials, UserAlreadyExists, TokenExpired
from backend.models.user import User
from backend.schemas.user import UserRegister, TokenResponse


async def register_user(db: AsyncSession, data: UserRegister, bg_tasks: BackgroundTasks) -> tuple[User, TokenResponse]:
    """Register a new user and return tokens immediately."""
    existing = await db.execute(
        select(User).where((User.username == data.username) | (User.email == data.email))
    )
    if existing.scalar_one_or_none():
        raise UserAlreadyExists()

    user = User(
        username=data.username,
        email=data.email,
        password_hash=hash_password(data.password),
        is_verified=True,  # Auto-verify for now
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    tokens = _create_tokens(user)
    return user, tokens


async def login_user(db: AsyncSession, username: str, password: str) -> tuple[User, TokenResponse]:
    """Authenticate user and return tokens."""
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(password, user.password_hash):
        raise InvalidCredentials()

    tokens = _create_tokens(user)
    return user, tokens


async def refresh_tokens(db: AsyncSession, refresh_token: str) -> TokenResponse:
    """Issue new access + refresh tokens from a valid refresh token."""
    payload = decode_token(refresh_token)
    if payload.get("type") != "refresh":
        raise InvalidCredentials()

    user_id = payload["sub"]
    result = await db.execute(select(User).where(User.id == uuid.UUID(user_id)))
    user = result.scalar_one_or_none()
    if not user:
        raise InvalidCredentials()

    return _create_tokens(user)


async def get_user_by_id(db: AsyncSession, user_id: uuid.UUID) -> User | None:
    """Fetch user by ID."""
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


def _create_tokens(user: User) -> TokenResponse:
    """Generate access and refresh token pair."""
    subject = str(user.id)
    return TokenResponse(
        access_token=create_access_token(subject, extra={"username": user.username}),
        refresh_token=create_refresh_token(subject),
    )

async def verify_email(db: AsyncSession, token: str) -> None:
    """Verify an email token and activate the user's account."""
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    
    result = await db.execute(
        select(User).where(User.verification_token_hash == token_hash)
    )
    user = result.scalar_one_or_none()

    from fastapi import HTTPException
    if not user:
        raise HTTPException(status_code=400, detail="Invalid verification token.")

    if not user.verification_token_expires_at:
        raise HTTPException(status_code=400, detail="Token already used or invalid.")

    if datetime.now(timezone.utc) > user.verification_token_expires_at:
        raise HTTPException(status_code=400, detail="Verification token has expired. Please request a new one.")

    # Mark as verified
    user.is_verified = True
    user.verification_token_hash = None
    user.verification_token_expires_at = None
    
    await db.commit()

async def resend_verification_email(db: AsyncSession, username: str, bg_tasks: BackgroundTasks) -> None:
    """Generate a new verification token and resend the email if user is unverified."""
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    
    from fastapi import HTTPException
    if not user:
        raise HTTPException(status_code=404, detail="No user found with this username.")
    if user.is_verified:
        raise HTTPException(status_code=400, detail="Account is already verified.")
        
    # Generate new verification token
    raw_token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=30)
    
    user.verification_token_hash = token_hash
    user.verification_token_expires_at = expires_at
    await db.commit()
    
    # Queue email in background
    from backend.services.email_service import send_verification_email
    bg_tasks.add_task(send_verification_email, user.email, raw_token)
