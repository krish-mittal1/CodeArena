"""AI insight library routes."""

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.session import get_db
from backend.dependencies import get_current_user
from backend.models.ai_analysis import AIAnalysis
from backend.models.user import User

router = APIRouter(prefix="/insights", tags=["Insights"])


@router.get("")
async def list_insights(
    q: Optional[str] = Query(None),
    topic: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = (
        select(AIAnalysis)
        .where(AIAnalysis.user_id == current_user.id)
        .order_by(AIAnalysis.created_at.desc())
        .limit(limit)
    )
    if topic:
        query = query.where(AIAnalysis.topic == topic)
    result = await db.execute(query)
    rows = result.scalars().all()

    items = []
    for row in rows:
        if q and q.lower() not in row.problem_title.lower():
            continue
        items.append({
            "id": str(row.id),
            "submission_id": str(row.submission_id) if row.submission_id else None,
            "problem_id": str(row.problem_id),
            "problem_title": row.problem_title,
            "topic": row.topic,
            "verdict": row.verdict,
            "tip": (row.analysis.get("tips") or [""])[0] if row.analysis else "",
            "pattern": row.analysis.get("optimized_approach", "")[:200] if row.analysis else "",
            "share_slug": row.share_slug,
            "created_at": row.created_at.isoformat(),
        })
    return {"insights": items}


@router.get("/share/{share_slug}")
async def get_shared_insight(share_slug: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AIAnalysis).where(AIAnalysis.share_slug == share_slug))
    row = result.scalar_one_or_none()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Insight not found")
    return {
        "problem_title": row.problem_title,
        "topic": row.topic,
        "verdict": row.verdict,
        "analysis": {
            "problem_concept": row.analysis.get("problem_concept", ""),
            "tips": row.analysis.get("tips", []),
            "optimized_approach": row.analysis.get("optimized_approach", ""),
        },
    }


@router.get("/{insight_id}")
async def get_insight(
    insight_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(AIAnalysis).where(AIAnalysis.id == insight_id, AIAnalysis.user_id == current_user.id)
    )
    row = result.scalar_one_or_none()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Insight not found")
    return {
        "id": str(row.id),
        "problem_id": str(row.problem_id),
        "problem_title": row.problem_title,
        "topic": row.topic,
        "verdict": row.verdict,
        "analysis": row.analysis,
        "share_slug": row.share_slug,
        "created_at": row.created_at.isoformat(),
    }
