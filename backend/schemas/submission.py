"""Submission schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from backend.core.constants import Language


class SubmissionCreate(BaseModel):
    match_id: uuid.UUID
    code: str = Field(..., min_length=1, max_length=50000)
    language: Language


class SubmissionResponse(BaseModel):
    id: uuid.UUID
    match_id: uuid.UUID
    user_id: uuid.UUID
    language: str
    status: str
    passed_test_cases: int
    total_test_cases: int
    execution_time_ms: int | None = None
    memory_used_kb: int | None = None
    submitted_at: datetime
    judged_at: datetime | None = None

    model_config = {"from_attributes": True}


class SubmissionResultResponse(BaseModel):
    test_case_order: int
    verdict: str
    execution_time_ms: int
    memory_used_kb: int
