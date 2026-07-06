"""User schemas."""

import re
import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator


# ── Requests ──────────────────────────────────────────────────

class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_]+$")
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)

    @field_validator('password')
    @classmethod
    def password_complexity(cls, v):
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain at least one digit')
        return v

class UserLogin(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=1, max_length=128)


# ── Responses ─────────────────────────────────────────────────

class UserPublic(BaseModel):
    id: uuid.UUID
    username: str
    elo: int
    matches_played: int
    matches_won: int

    model_config = {"from_attributes": True}


class UserProfile(UserPublic):
    email: str
    created_at: datetime
    onboarding_completed: bool = False
    preferred_track: str | None = None
    practice_streak: int = 0

    model_config = {"from_attributes": True}


class OnboardingComplete(BaseModel):
    track: str = Field(..., pattern=r"^(interview|cp|battle)$")
    start_tutorial_match: bool = False


class UserStats(BaseModel):
    username: str
    elo: int
    matches_played: int
    matches_won: int
    win_rate: float

    model_config = {"from_attributes": True}


# ── Auth Tokens ───────────────────────────────────────────────

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefresh(BaseModel):
    refresh_token: str
