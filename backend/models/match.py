"""Match model."""

import uuid
from datetime import datetime, timezone
from typing import Optional, List, TYPE_CHECKING

from sqlalchemy import String, Integer, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.db.base import Base
from backend.core.constants import MatchStatus

if TYPE_CHECKING:
    from backend.models.match_problem import MatchProblem
    from backend.models.user import User
    from backend.models.problem import Problem
    from backend.models.submission import Submission


class Match(Base):
    __tablename__ = "matches"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    player1_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    player2_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    problem_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("problems.id"), nullable=False
    )
    winner_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    status: Mapped[str] = mapped_column(
        String(20), default=MatchStatus.PENDING, nullable=False
    )
    player1_elo_before: Mapped[int] = mapped_column(Integer, nullable=False)
    player2_elo_before: Mapped[int] = mapped_column(Integer, nullable=False)
    player1_elo_after: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    player2_elo_after: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=900)

    # Relationships
    player1: Mapped["User"] = relationship("User", foreign_keys=[player1_id])
    player2: Mapped["User"] = relationship("User", foreign_keys=[player2_id])
    # Legacy single-problem FK kept as first problem for backward compatibility
    problem: Mapped["Problem"] = relationship("Problem")
    match_problems: Mapped[List["MatchProblem"]] = relationship(
        "MatchProblem",
        back_populates="match",
        cascade="all, delete-orphan",
        order_by="MatchProblem.order_index",
    )
    winner: Mapped[Optional["User"]] = relationship("User", foreign_keys=[winner_id])
    submissions: Mapped[List["Submission"]] = relationship(back_populates="match")

    __table_args__ = (
        Index("idx_matches_players", "player1_id", "player2_id"),
        Index(
            "idx_matches_status_active",
            "status",
            postgresql_where=(status == MatchStatus.ACTIVE),
        ),
    )

    def __repr__(self) -> str:
        return f"<Match {self.id} {self.status}>"
