"""Match schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel

from backend.schemas.user import UserPublic


class MatchResponse(BaseModel):
    id: uuid.UUID
    player1: UserPublic
    player2: UserPublic
    problem_id: uuid.UUID
    status: str
    winner_id: uuid.UUID | None = None
    player1_elo_before: int
    player2_elo_before: int
    player1_elo_after: int | None = None
    player2_elo_after: int | None = None
    started_at: datetime
    ended_at: datetime | None = None
    duration_seconds: int

    model_config = {"from_attributes": True}


class MatchHistoryItem(BaseModel):
    id: uuid.UUID
    opponent_username: str
    opponent_elo: int
    your_elo_before: int
    your_elo_after: int | None
    result: str  # "win" | "loss" | "draw"
    started_at: datetime
    duration_seconds: int


class MatchSummary(BaseModel):
    match_id: uuid.UUID
    status: str
    remaining_seconds: int | None = None
