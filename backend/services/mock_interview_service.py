"""In-memory mock interview sessions (single-server)."""

from __future__ import annotations

import random
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.problem import Problem

_sessions: dict[str, "MockSession"] = {}


@dataclass
class MockSession:
    id: str
    user_id: str
    company: str
    problem_ids: list[str]
    problem_titles: list[str]
    problem_difficulties: list[str]
    started_at: datetime
    duration_minutes: int = 45
    submissions: dict[str, str] = field(default_factory=dict)  # problem_id -> submission_id


async def start_mock_interview(
    db: AsyncSession,
    user_id: uuid.UUID,
    company: str = "Google",
) -> dict:
    result = await db.execute(
        select(Problem).where(Problem.is_active.is_(True), Problem.problem_type == "dsa")
    )
    problems = list(result.scalars().all())
    easy = [p for p in problems if p.difficulty == "easy"]
    medium = [p for p in problems if p.difficulty == "medium"]
    if not easy or not medium:
        raise ValueError("Not enough problems for mock interview")

    p1 = random.choice(easy)
    p2 = random.choice(medium)
    session_id = str(uuid.uuid4())
    session = MockSession(
        id=session_id,
        user_id=str(user_id),
        company=company,
        problem_ids=[str(p1.id), str(p2.id)],
        problem_titles=[p1.title, p2.title],
        problem_difficulties=[p1.difficulty, p2.difficulty],
        started_at=datetime.now(timezone.utc),
    )
    _sessions[session_id] = session
    return {
        "session_id": session_id,
        "company": company,
        "duration_minutes": session.duration_minutes,
        "problems": [
            {"id": str(p1.id), "title": p1.title, "difficulty": p1.difficulty, "order": 1},
            {"id": str(p2.id), "title": p2.title, "difficulty": p2.difficulty, "order": 2},
        ],
    }


def get_session(session_id: str, user_id: uuid.UUID) -> Optional[MockSession]:
    s = _sessions.get(session_id)
    if s and s.user_id == str(user_id):
        return s
    return None


def record_submission(session_id: str, problem_id: str, submission_id: str) -> None:
    s = _sessions.get(session_id)
    if s:
        s.submissions[problem_id] = submission_id
