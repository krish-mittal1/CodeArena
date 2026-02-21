"""User schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


# ── Requests ──────────────────────────────────────────────────

class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_]+$")
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)


class UserLogin(BaseModel):
    username: str
    password: str


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

    model_config = {"from_attributes": True}


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
