"""Problem model."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Text, Integer, Boolean, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from typing import Optional, Dict

from backend.db.base import Base
from backend.core.constants import Difficulty


class Problem(Base):
    __tablename__ = "problems"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    difficulty: Mapped[str] = mapped_column(String(20), nullable=False, default=Difficulty.MEDIUM)
    input_format: Mapped[str] = mapped_column(Text, nullable=False)
    output_format: Mapped[str] = mapped_column(Text, nullable=False)
    constraints: Mapped[str] = mapped_column(Text, nullable=True)
    problem_type: Mapped[str] = mapped_column(
        String(20), nullable=False, default="dsa", server_default="dsa"
    )
    
    # ── LeetCode Execution Architecture ──
    method_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    parameters: Mapped[Optional[Dict]] = mapped_column(JSONB, nullable=True)
    return_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    time_limit_ms: Mapped[int] = mapped_column(Integer, default=2000, nullable=False)
    memory_limit_mb: Mapped[int] = mapped_column(Integer, default=256, nullable=False)
    rating: Mapped[int] = mapped_column(Integer, default=800, nullable=False, doc="Internal CF-style rating (800-1200), hidden from users")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    test_cases: Mapped[list["TestCase"]] = relationship(
        back_populates="problem", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_problems_active", "is_active", postgresql_where=(is_active == True)),
    )

    def __repr__(self) -> str:
        return f"<Problem {self.title}>"
