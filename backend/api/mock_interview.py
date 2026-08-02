"""Mock interview simulation routes."""

import uuid
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.session import get_db
from backend.dependencies import get_current_user, get_redis
from backend.models.submission import Submission
from backend.models.user import User
from backend.services import ai_service, mock_interview_service, problem_service

router = APIRouter(prefix="/mock-interview", tags=["MockInterview"])

# Cap debrief LLM fan-out so one request cannot burn unbounded analysis quota.
_MAX_DEBRIEF_SUBMISSIONS = 5


class MockStartRequest(BaseModel):
    company: str = Field(default="Google", max_length=80)


class MockDebriefRequest(BaseModel):
    session_id: str
    submission_ids: list[uuid.UUID] = Field(default_factory=list, max_length=_MAX_DEBRIEF_SUBMISSIONS)


class MockRecordRequest(BaseModel):
    problem_id: uuid.UUID
    submission_id: uuid.UUID


@router.post("/start")
async def start_mock(
    data: MockStartRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        return await mock_interview_service.start_mock_interview(db, current_user.id, data.company)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.get("/session/{session_id}")
async def get_mock_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
):
    session = mock_interview_service.get_session(session_id, current_user.id)
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    difficulties = getattr(session, "problem_difficulties", None) or ["medium"] * len(session.problem_ids)
    submission_ids = [
        session.submissions.get(pid)
        for pid in session.problem_ids
    ]
    return {
        "session_id": session.id,
        "company": session.company,
        "duration_minutes": session.duration_minutes,
        "problems": [
            {
                "id": pid,
                "title": title,
                "difficulty": difficulties[i] if i < len(difficulties) else "medium",
                "order": i + 1,
                "submission_id": session.submissions.get(pid),
            }
            for i, (pid, title) in enumerate(zip(session.problem_ids, session.problem_titles))
        ],
        "submission_ids": [sid for sid in submission_ids if sid],
        "started_at": session.started_at.isoformat(),
    }


@router.post("/session/{session_id}/record")
async def record_mock_submission(
    session_id: str,
    data: MockRecordRequest,
    current_user: User = Depends(get_current_user),
):
    session = mock_interview_service.get_session(session_id, current_user.id)
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    if str(data.problem_id) not in session.problem_ids:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Problem not in this session")
    mock_interview_service.record_submission(session_id, str(data.problem_id), str(data.submission_id))
    return {"ok": True}


@router.post("/debrief")
async def mock_debrief(
    data: MockDebriefRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    redis: Optional[Redis] = Depends(get_redis),
) -> Any:
    """
    Debrief a mock interview session.

    Quota policy: one analysis slot per debrief request (not per problem).
    Slot is acquired up front; released if no successful LLM call was needed
    (all cache hits / fallbacks). Caps submission_ids at 5 to bound LLM fan-out.
    """
    from backend.core.ai_rate_limit import (
        ensure_analysis_allowed,
        record_analysis_use,
        release_analysis_slot,
    )

    session = mock_interview_service.get_session(data.session_id, current_user.id)
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    # One slot per debrief when any submission may need an LLM call.
    needs_llm = any(
        not ai_service.has_cached_analysis(str(sub_id)) for sub_id in data.submission_ids
    )
    reservation = None
    if needs_llm:
        reservation = await ensure_analysis_allowed(str(current_user.id), redis=redis)

    used_llm_any = False
    summaries = []

    try:
        for sub_id in data.submission_ids:
            result = await db.execute(
                select(Submission).where(Submission.id == sub_id, Submission.user_id == current_user.id)
            )
            sub = result.scalar_one_or_none()
            if not sub:
                continue
            problem = await problem_service.get_problem_by_id(db, sub.problem_id)
            if not problem:
                continue
            outcome = await ai_service.analyze_code(
                problem_title=problem.title,
                problem_description=problem.description,
                constraints=getattr(problem, "constraints", None),
                language=sub.language,
                code=sub.code,
                verdict_status=sub.status,
                submission_id=str(sub.id),
            )
            if outcome.used_llm:
                used_llm_any = True
            summaries.append({
                "problem_title": problem.title,
                "verdict": sub.status,
                "analysis": outcome.analysis,
            })
    except Exception:
        if reservation is not None:
            await release_analysis_slot(str(current_user.id), reservation, redis=redis)
        raise

    if reservation is not None:
        if used_llm_any:
            await record_analysis_use(
                str(current_user.id), redis=redis, reservation=reservation
            )
        else:
            await release_analysis_slot(str(current_user.id), reservation, redis=redis)

    hire_signal = "lean_hire" if any(s["verdict"] == "accepted" for s in summaries) else "lean_no_hire"
    return {
        "company": session.company,
        "hire_signal": hire_signal,
        "rubric": {
            "correctness": "Strong" if hire_signal == "lean_hire" else "Needs work",
            "complexity": "Review AI feedback per problem",
            "communication": "Practice explaining your approach out loud",
        },
        "problem_summaries": summaries,
    }
