"""Mock interview simulation routes."""

import uuid
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.session import get_db
from backend.dependencies import get_current_user
from backend.models.submission import Submission
from backend.models.user import User
from backend.services import ai_service, mock_interview_service, problem_service
from backend.services.interview_metadata_service import get_problem_meta

router = APIRouter(prefix="/mock-interview", tags=["MockInterview"])


class MockStartRequest(BaseModel):
    company: str = Field(default="Google", max_length=80)


class MockDebriefRequest(BaseModel):
    session_id: str
    submission_ids: list[uuid.UUID] = Field(default_factory=list)


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
) -> Any:
    session = mock_interview_service.get_session(data.session_id, current_user.id)
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    summaries = []
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
        analysis = await ai_service.analyze_code(
            problem_title=problem.title,
            problem_description=problem.description,
            constraints=getattr(problem, "constraints", None),
            language=sub.language,
            code=sub.code,
            verdict_status=sub.status,
            submission_id=str(sub.id),
        )
        summaries.append({
            "problem_title": problem.title,
            "verdict": sub.status,
            "analysis": analysis,
        })

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
