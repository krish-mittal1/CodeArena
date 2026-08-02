"""Match schemas."""

import uuid
from datetime import datetime

from typing import Optional, Union
from pydantic import BaseModel

from backend.schemas.user import UserPublic


class MatchProblemBrief(BaseModel):
    id: uuid.UUID
    title: str
    difficulty: Optional[str] = None
    order_index: int = 0


class MatchResponse(BaseModel):
    id: uuid.UUID
    player1: UserPublic
    player2: UserPublic
    problem_id: uuid.UUID
    problems: list[MatchProblemBrief] = []
    solved_problem_ids: list[uuid.UUID] = []
    status: str
    winner_id: Optional[uuid.UUID] = None
    player1_elo_before: int
    player2_elo_before: int
    player1_elo_after: Optional[int] = None
    player2_elo_after: Optional[int] = None
    started_at: datetime
    ended_at: Optional[datetime] = None
    duration_seconds: int

    model_config = {"from_attributes": True}


class MatchHistoryItem(BaseModel):
    id: uuid.UUID
    opponent_username: str
    opponent_elo: int
    your_elo_before: int
    your_elo_after: Optional[int]
    result: str  # "win" | "loss" | "draw"
    started_at: datetime
    duration_seconds: int


class MatchSummary(BaseModel):
    match_id: uuid.UUID
    status: str
    remaining_seconds: Optional[int] = None
