"""
Match routes — match details and history.
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import Optional, List
from redis.asyncio import Redis

from backend.db.session import get_db, AsyncSession
from backend.dependencies import get_current_user, get_redis
from backend.models.user import User
from backend.schemas.match import MatchResponse, MatchHistoryItem, MatchProblemBrief
from backend.services import match_service
from backend.websocket.manager import manager

router = APIRouter(prefix="/matches", tags=["Matches"])


@router.get("/recap/{match_id}")
async def get_match_recap(
    match_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Public read-only match recap for share links."""
    recap = await match_service.get_match_recap(db, match_id)
    if not recap:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match recap not available")
    return recap


@router.get("/{match_id}", response_model=MatchResponse)
async def get_match(
    match_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get match details by ID. Only participants can view match details."""
    match = await match_service.get_match(db, match_id)
    
    # ✓ FIXED: Strict access control - only participants
    if current_user.id not in (match.player1_id, match.player2_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this match",
        )

    problems = [
        MatchProblemBrief(
            id=uuid.UUID(str(item["id"])),
            title=item["title"],
            difficulty=item.get("difficulty"),
            order_index=item.get("order_index", 0),
        )
        for item in match_service.match_problem_summaries(match)
    ]

    from backend.models.submission import Submission
    from backend.core.constants import SubmissionStatus
    from sqlalchemy import select

    problem_ids = match_service.get_match_problem_ids(match)
    solved_problem_ids: list[uuid.UUID] = []
    if problem_ids:
        solved_rows = await db.execute(
            select(Submission.problem_id)
            .where(
                Submission.match_id == match.id,
                Submission.user_id == current_user.id,
                Submission.status == SubmissionStatus.ACCEPTED,
                Submission.problem_id.in_(problem_ids),
            )
            .distinct()
        )
        solved_problem_ids = list(solved_rows.scalars().all())

    return MatchResponse(
        id=match.id,
        player1=match.player1,
        player2=match.player2,
        problem_id=match.problem_id,
        problems=problems,
        solved_problem_ids=solved_problem_ids,
        status=match.status,
        winner_id=match.winner_id,
        player1_elo_before=match.player1_elo_before,
        player2_elo_before=match.player2_elo_before,
        player1_elo_after=match.player1_elo_after,
        player2_elo_after=match.player2_elo_after,
        started_at=match.started_at,
        ended_at=match.ended_at,
        duration_seconds=match.duration_seconds,
    )


@router.get("/history/me", response_model=List[MatchHistoryItem])
async def get_match_history(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get match history for the current user."""
    matches = await match_service.get_match_history(db, current_user.id, limit, offset)
    user_id = current_user.id

    history = []
    for m in matches:
        is_player1 = m.player1_id == user_id
        opponent = m.player2 if is_player1 else m.player1
        elo_before = m.player1_elo_before if is_player1 else m.player2_elo_before
        elo_after = m.player1_elo_after if is_player1 else m.player2_elo_after

        if m.winner_id is None:
            result = "draw"
        elif m.winner_id == user_id:
            result = "win"
        else:
            result = "loss"

        history.append(MatchHistoryItem(
            id=m.id,
            opponent_username=opponent.username,
            opponent_elo=opponent.elo,
            your_elo_before=elo_before,
            your_elo_after=elo_after,
            result=result,
            started_at=m.started_at,
            duration_seconds=m.duration_seconds,
        ))

    return history


@router.post("/{match_id}/forfeit")
async def forfeit_match(
    match_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    redis: Optional[Redis] = Depends(get_redis),
):
    """
    Forfeit an active match.

    Behavior:
      - Only participants can forfeit
      - If match already completed → no-op (idempotent)
      - Opponent is declared winner and ELO updated
      - WebSocket match_ended is sent to both players (and spectators)
    """
    result = await match_service.forfeit_match(db, redis, match_id, current_user.id)

    # Already completed / non-active → treat as success, nothing to broadcast
    if not result:
        return {"status": "already_completed"}

    room_id = str(match_id)

    # Personalized match_ended (local + Redis pub/sub for other pods)
    await manager.broadcast_match_ended(room_id, result)

    # Dev-mode matchmaking uses in-memory active_matches tracking; clear it safely
    if redis is None:
        try:
            from backend.services.matchmaking_memory import memory_queue

            await memory_queue.clear_match_for_both(result["player1_id"], result["player2_id"])
        except Exception:
            # Best-effort cleanup — stale mappings are tolerated
            pass

    return {"status": "forfeited"}
