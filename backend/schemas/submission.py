"""Submission schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field, field_validator
from typing import Optional, Union

from backend.core.constants import Language


class FailedTestCaseDetails(BaseModel):
    input: str
    expected_output: str
    actual_output: Optional[str] = None
    error_output: Optional[str] = None


class SubmissionCreate(BaseModel):
    match_id: uuid.UUID
    code: str = Field(..., min_length=1, max_length=50000)
    language: Language
    
    @field_validator("code")
    @classmethod
    def validate_code(cls, v: str) -> str:
        """Validate code submission to prevent injection attacks."""
        # ✓ FIXED: Validate code doesn't contain suspicious patterns
        if v.count('\n') > 5000:  # Prevent extremely long files
            raise ValueError("Code submission too large")
        if len(v.split('\n')) > 5000:  # Prevent file bombs
            raise ValueError("Code has too many lines")
        # Check for null bytes (injection attempt)
        if '\x00' in v:
            raise ValueError("Invalid code format")
        return v.strip()


class SubmissionResponse(BaseModel):
    id: uuid.UUID
    match_id: Optional[uuid.UUID] = None
    user_id: uuid.UUID
    language: str
    status: str
    passed_test_cases: int
    total_test_cases: int
    execution_time_ms: Optional[int] = None
    memory_used_kb: Optional[int] = None
    submitted_at: datetime
    judged_at: Optional[datetime] = None
    failed_test_case: Optional[FailedTestCaseDetails] = None

    model_config = {"from_attributes": True}


class SubmissionResultResponse(BaseModel):
    test_case_order: int
    verdict: str
    execution_time_ms: int
    memory_used_kb: int
