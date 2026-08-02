"""Match ↔ Problem association (ordered multi-problem battles)."""

import uuid

from sqlalchemy import Integer, ForeignKey, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.db.base import Base


class MatchProblem(Base):
    __tablename__ = "match_problems"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    match_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("matches.id", ondelete="CASCADE"),
        nullable=False,
    )
    problem_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("problems.id", ondelete="RESTRICT"),
        nullable=False,
    )
    order_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    match: Mapped["Match"] = relationship("Match", back_populates="match_problems")
    problem: Mapped["Problem"] = relationship("Problem")

    __table_args__ = (
        UniqueConstraint("match_id", "order_index", name="uq_match_problems_order"),
        UniqueConstraint("match_id", "problem_id", name="uq_match_problems_problem"),
        Index("idx_match_problems_match_id", "match_id"),
    )

    def __repr__(self) -> str:
        return f"<MatchProblem match={self.match_id} order={self.order_index}>"
