"""SubmissionResult model — per-test-case verdict."""

import uuid

from sqlalchemy import String, Text, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.db.base import Base


class SubmissionResult(Base):
    __tablename__ = "submission_results"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    submission_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("submissions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    test_case_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("test_cases.id"), nullable=False
    )
    verdict: Mapped[str] = mapped_column(String(30), nullable=False)
    execution_time_ms: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    memory_used_kb: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    actual_output: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_output: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    submission: Mapped["Submission"] = relationship(back_populates="results")
    test_case: Mapped["TestCase"] = relationship("TestCase")

    def __repr__(self) -> str:
        return f"<SubmissionResult {self.verdict}>"
