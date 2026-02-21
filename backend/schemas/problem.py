"""Problem schemas."""

import uuid

from pydantic import BaseModel, Field

from backend.core.constants import Difficulty


class TestCaseCreate(BaseModel):
    input: str
    expected_output: str
    is_sample: bool = False
    order_index: int = 0


class ProblemCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str
    difficulty: Difficulty = Difficulty.MEDIUM
    input_format: str
    output_format: str
    constraints: str | None = None
    time_limit_ms: int = Field(2000, ge=500, le=10000)
    memory_limit_mb: int = Field(256, ge=32, le=512)
    test_cases: list[TestCaseCreate] = Field(..., min_length=1)


class TestCasePublic(BaseModel):
    input: str
    expected_output: str
    order_index: int

    model_config = {"from_attributes": True}


class ProblemPublic(BaseModel):
    id: uuid.UUID
    title: str
    description: str
    difficulty: str
    input_format: str
    output_format: str
    constraints: str | None
    time_limit_ms: int
    memory_limit_mb: int
    sample_cases: list[TestCasePublic] = []

    model_config = {"from_attributes": True}


class ProblemAdmin(ProblemPublic):
    """Admin view includes all test cases and metadata."""
    is_active: bool
    all_test_cases: list[TestCasePublic] = []

    model_config = {"from_attributes": True}
