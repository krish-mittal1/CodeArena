"""Submission model."""

import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict

from sqlalchemy import String, Text, Integer, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.db.base import Base
from backend.core.constants import SubmissionStatus


class Submission(Base):
    __tablename__ = "submissions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    match_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("matches.id", ondelete="CASCADE"), nullable=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    problem_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("problems.id"), nullable=False
    )
    language: Mapped[str] = mapped_column(String(20), nullable=False)
    code: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(
        String(30), default=SubmissionStatus.QUEUED, nullable=False
    )
    passed_test_cases: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_test_cases: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    execution_time_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    memory_used_kb: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    judged_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    match: Mapped["Match"] = relationship(back_populates="submissions")
    user: Mapped["User"] = relationship(back_populates="submissions")
    problem: Mapped["Problem"] = relationship("Problem")
    results: Mapped[List["SubmissionResult"]] = relationship(
        back_populates="submission", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_submissions_match_user", "match_id", "user_id"),
        Index("idx_submissions_user_id", "user_id"),
        Index("idx_submissions_problem_id", "problem_id"),
        Index(
            "idx_submissions_status_pending",
            "status",
            postgresql_where=(status.in_([SubmissionStatus.QUEUED, SubmissionStatus.RUNNING])),
        ),
    )

    @property
    def failed_test_case(self) -> Optional[Dict[str, Optional[str]]]:
        if self.status in [SubmissionStatus.ACCEPTED, SubmissionStatus.QUEUED, SubmissionStatus.RUNNING]:
            return None
            
        try:
            # Assumes self.results and self.results[i].test_case are eager loaded
            for result in sorted(self.results, key=lambda r: r.test_case.order_index):
                if result.verdict != "accepted":
                    return {
                        "input": result.test_case.input,
                        "expected_output": result.test_case.expected_output,
                        "actual_output": result.actual_output,
                        "error_output": result.error_output
                    }
        except Exception:
            pass # fallback if relationship not loaded
        return None

    def __repr__(self) -> str:
        return f"<Submission {self.id} {self.status}>"
