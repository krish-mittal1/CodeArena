"""
Rating service — ELO calculation and atomic database updates.
"""

from typing import Optional
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.constants import ELO_FLOOR
from backend.models.user import User

# Fixed K-factor for all players
ELO_K = 32


def calculate_expected_score(rating_a: int, rating_b: int) -> float:
    """Calculate expected score for player A against player B."""
    return 1.0 / (1.0 + 10 ** ((rating_b - rating_a) / 400.0))


def calculate_elo_delta(
    rating_a: int,
    rating_b: int,
    actual_score: float,
) -> int:
    """
    Calculate ELO rating change for a player.

    Args:
        rating_a: Current rating of the player
        rating_b: Current rating of the opponent
        actual_score: 1.0 for win, 0.0 for loss, 0.5 for draw

    Returns:
        Integer ELO delta (can be negative)
    """
    expected = calculate_expected_score(rating_a, rating_b)
    return round(ELO_K * (actual_score - expected))


async def update_ratings(
    db: AsyncSession,
    player1_id: uuid.UUID,
    player2_id: uuid.UUID,
    winner_id: Optional[uuid.UUID],
) -> tuple[int, int, int, int]:
    """
    Atomically update both players' ELO ratings after a match.

    Uses SELECT ... FOR UPDATE to prevent concurrent modification.

    Args:
        winner_id: UUID of the winner, or None for a draw.

    Returns:
        (p1_new_elo, p2_new_elo, p1_delta, p2_delta)
    """
    # Lock both rows to prevent concurrent updates
    result = await db.execute(
        select(User)
        .where(User.id.in_([player1_id, player2_id]))
        .with_for_update()
    )
    users = {u.id: u for u in result.scalars().all()}

    p1 = users[player1_id]
    p2 = users[player2_id]

    # Determine actual scores
    if winner_id is None:
        # Draw
        score_p1, score_p2 = 0.5, 0.5
    elif winner_id == player1_id:
        score_p1, score_p2 = 1.0, 0.0
    else:
        score_p1, score_p2 = 0.0, 1.0

    # Calculate deltas
    delta_p1 = calculate_elo_delta(p1.elo, p2.elo, score_p1)
    delta_p2 = calculate_elo_delta(p2.elo, p1.elo, score_p2)

    # Apply with floor
    p1_new = max(ELO_FLOOR, p1.elo + delta_p1)
    p2_new = max(ELO_FLOOR, p2.elo + delta_p2)

    # Update
    p1.elo = p1_new
    p1.matches_played += 1
    if winner_id == player1_id:
        p1.matches_won += 1

    p2.elo = p2_new
    p2.matches_played += 1
    if winner_id == player2_id:
        p2.matches_won += 1

    await db.flush()

    return p1_new, p2_new, delta_p1, delta_p2
