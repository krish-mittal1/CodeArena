"""
Auth routes — register, login, refresh tokens.
"""

from fastapi import APIRouter, Depends, Query, BackgroundTasks

from backend.db.session import get_db, AsyncSession
from backend.schemas.user import UserRegister, UserLogin, TokenResponse, TokenRefresh, UserProfile
from backend.services import auth_service

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(data: UserRegister, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    """Register a new user account."""
    _, tokens = await auth_service.register_user(db, data, background_tasks)
    return tokens

@router.get("/verify-email")
async def verify_email(token: str = Query(...), db: AsyncSession = Depends(get_db)):
    """Verify user email with token."""
    await auth_service.verify_email(db, token)
    return {"message": "Email verified successfully. You can now log in."}

from backend.schemas.user import ResendVerificationRequest
@router.post("/resend-verification")
async def resend_verification(data: ResendVerificationRequest, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    """Resend a new verification email to the user."""
    await auth_service.resend_verification_email(db, data.username, background_tasks)
    return {"message": "If the account exists and is not verified, a new verification link has been sent."}


@router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin, db: AsyncSession = Depends(get_db)):
    """Login with username and password."""
    _, tokens = await auth_service.login_user(db, data.username, data.password)
    return tokens


@router.post("/refresh", response_model=TokenResponse)
async def refresh(data: TokenRefresh, db: AsyncSession = Depends(get_db)):
    """Refresh access token using a valid refresh token."""
    return await auth_service.refresh_tokens(db, data.refresh_token)
