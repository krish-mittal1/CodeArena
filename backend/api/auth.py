"""
Auth routes — register, login, refresh tokens.
"""

from fastapi import APIRouter, Depends, BackgroundTasks, Request
from backend.db.session import get_db, AsyncSession
from backend.schemas.user import UserRegister, UserLogin, TokenResponse, TokenRefresh
from backend.services import auth_service
from backend.dependencies import get_client_ip
from backend.core.auth_rate_limit import (
    ensure_login_allowed,
    record_login_failure,
    clear_login_failures,
)
from backend.core.exceptions import InvalidCredentials

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(
    data: UserRegister, 
    background_tasks: BackgroundTasks, 
    db: AsyncSession = Depends(get_db)
):
    """Register a new user account."""
    # Note: verify_email and other background tasks are handled inside register_user
    _, tokens = await auth_service.register_user(db, data, background_tasks)
    return tokens


@router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin, request: Request, db: AsyncSession = Depends(get_db)):
    """Login with username and password."""
    ip = get_client_ip(request)
    ensure_login_allowed(data.username, ip)
    try:
        _, tokens = await auth_service.login_user(db, data.username, data.password)
    except InvalidCredentials:
        record_login_failure(data.username, ip)
        raise
    clear_login_failures(data.username, ip)
    return tokens


@router.post("/refresh", response_model=TokenResponse)
async def refresh(data: TokenRefresh, db: AsyncSession = Depends(get_db)):
    """Refresh access token using a valid refresh token."""
    return await auth_service.refresh_tokens(db, data.refresh_token)
