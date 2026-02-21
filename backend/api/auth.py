"""
Auth routes — register, login, refresh tokens.
"""

from fastapi import APIRouter, Depends

from backend.db.session import get_db, AsyncSession
from backend.schemas.user import UserRegister, UserLogin, TokenResponse, TokenRefresh, UserProfile
from backend.services import auth_service

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(data: UserRegister, db: AsyncSession = Depends(get_db)):
    """Register a new user account."""
    _, tokens = await auth_service.register_user(db, data)
    return tokens


@router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin, db: AsyncSession = Depends(get_db)):
    """Login with username and password."""
    _, tokens = await auth_service.login_user(db, data.username, data.password)
    return tokens


@router.post("/refresh", response_model=TokenResponse)
async def refresh(data: TokenRefresh, db: AsyncSession = Depends(get_db)):
    """Refresh access token using a valid refresh token."""
    return await auth_service.refresh_tokens(db, data.refresh_token)
