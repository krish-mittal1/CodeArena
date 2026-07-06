"""
User routes — profile, stats.
"""

import uuid
from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.dependencies import get_current_user
from backend.db.session import get_db
from backend.models.user import User
from backend.models.problem import Problem
from backend.schemas.user import UserProfile, UserStats, OnboardingComplete
from backend.services import progress_service, review_service

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


@router.post("/me/onboarding", response_model=UserProfile)
async def complete_onboarding(
    data: OnboardingComplete,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Mark onboarding complete and store the user's preferred track."""
    current_user.onboarding_completed = True
    current_user.preferred_track = data.track
    await db.commit()
    await db.refresh(current_user)
    return current_user


@router.get("/me/progress")
async def get_my_progress(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await progress_service.get_user_progress(db, current_user.id)


@router.get("/me/review-queue")
async def get_review_queue(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    items = await review_service.get_due_reviews(db, current_user.id)
    return {
        "items": items,
        "practice_streak": current_user.practice_streak,
    }


@router.post("/me/review-queue/{review_id}/complete")
async def complete_review_item(
    review_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await review_service.complete_review(db, current_user.id, review_id)
    await db.commit()
    return {"status": "ok"}


@router.get("/me/daily-problem")
async def get_daily_problem(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Problem).where(Problem.is_active.is_(True), Problem.problem_type == "dsa")
    )
    problems = list(result.scalars().all())
    pid = review_service.pick_daily_problem_id(problems)
    if not pid:
        return {"problem": None}
    problem = next((p for p in problems if p.id == pid), None)
    if not problem:
        return {"problem": None}
    return {
        "date": date.today().isoformat(),
        "practice_streak": current_user.practice_streak,
        "problem": {
            "id": str(problem.id),
            "title": problem.title,
            "difficulty": problem.difficulty,
        },
    }
