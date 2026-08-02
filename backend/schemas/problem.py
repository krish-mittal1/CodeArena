"""Problem schemas."""

import uuid

from typing import Optional, Any, List

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
    constraints: Optional[str] = None
    problem_type: str = "dsa"
    rating: int = Field(800, ge=800, le=3500)
    time_limit_ms: int = Field(2000, ge=500, le=10000)
    memory_limit_mb: int = Field(256, ge=32, le=512)
    test_cases: List[TestCaseCreate] = Field(..., min_length=1)


class TestCasePublic(BaseModel):
    input: str
    expected_output: str
    order_index: int
    explanation: Optional[str] = None

    model_config = {"from_attributes": True}


class ProblemExamplePublic(BaseModel):
    input: str
    output: str
    explanation: Optional[str] = None


class ProblemImagePublic(BaseModel):
    src: str
    alt: Optional[str] = None


class ProblemPublic(BaseModel):
    id: uuid.UUID
    title: str
    description: str
    difficulty: str
    input_format: str
    output_format: str
    constraints: Optional[str]
    problem_type: str = "dsa"
    rating: int = 800
    time_limit_ms: int
    memory_limit_mb: int
    method_name: Optional[str] = None
    parameters: Optional[Any] = None
    return_type: Optional[str] = None
    solved: bool = False
    sample_cases: List[TestCasePublic] = []
    examples: List[ProblemExamplePublic] = []
    images: List[ProblemImagePublic] = []

    model_config = {"from_attributes": True}


class ProblemCatalogPublic(BaseModel):
    id: uuid.UUID
    title: str
    difficulty: str
    problem_type: str = "dsa"
    rating: int = 800
    solved: bool = False

    model_config = {"from_attributes": True}


class ProblemAdmin(ProblemPublic):
    """Admin view includes all test cases and metadata."""
    is_active: bool
    all_test_cases: List[TestCasePublic] = []

    model_config = {"from_attributes": True}
