"""
User routes — profile, stats.
"""

from fastapi import APIRouter, Depends

from backend.dependencies import get_current_user
from backend.models.user import User
from backend.schemas.user import UserProfile, UserStats

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserProfile)
async def get_my_profile(current_user: User = Depends(get_current_user)):
    """Get the current user's profile."""
    return current_user


@router.get("/me/stats", response_model=UserStats)
async def get_my_stats(current_user: User = Depends(get_current_user)):
    """Get detailed stats for the current user."""
    win_rate = 0.0
    if current_user.matches_played > 0:
        win_rate = round(current_user.matches_won / current_user.matches_played * 100, 1)

    return UserStats(
        username=current_user.username,
        elo=current_user.elo,
        matches_played=current_user.matches_played,
        matches_won=current_user.matches_won,
        win_rate=win_rate,
    )
