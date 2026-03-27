from typing import Optional, Union
"""WebSocket event payload schemas."""

import uuid

from pydantic import BaseModel


# ── Server → Client ──────────────────────────────────────────

class WSMatchFound(BaseModel):
    match_id: uuid.UUID
    problem_id: uuid.UUID
    problem_title: str
    opponent_username: str
    opponent_elo: int
    duration_seconds: int


class WSTimerSync(BaseModel):
    remaining_seconds: int


class WSSubmissionQueued(BaseModel):
    submission_id: uuid.UUID


class WSSubmissionRunning(BaseModel):
    submission_id: uuid.UUID


class WSSubmissionResult(BaseModel):
    submission_id: uuid.UUID
    verdict: str
    passed: int
    total: int
    runtime_ms: Optional[int] = None
    memory_kb: Optional[int] = None


class WSOpponentSubmitted(BaseModel):
    verdict: str


class WSMatchEnded(BaseModel):
    winner_id: uuid.UUID | None
    reason: str  # "solved" | "timeout" | "forfeit"
    your_elo_delta: int
    new_elo: int


class WSError(BaseModel):
    code: str
    message: str


class WSSpectatorJoined(BaseModel):
    player1_username: str
    player2_username: str
    problem_title: str
    remaining_seconds: int


# ── Envelope ──────────────────────────────────────────────────

class WSMessage(BaseModel):
    """Standard envelope for all WebSocket messages."""
    event: str
    data: dict
