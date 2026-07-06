"""
Pydantic models for problem package meta.yaml files.
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field, model_validator


class ProblemParameter(BaseModel):
    name: str
    type: str


class GeneratorConfig(BaseModel):
    """Optional bulk test-case generation via generator.py in the package."""

    count: int = Field(default=0, ge=0)
    seed: int = 42


class ProblemPackageMeta(BaseModel):
    slug: str = Field(..., min_length=1, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    title: str = Field(..., min_length=1, max_length=200)
    problem_type: str = Field(default="dsa", pattern=r"^(dsa|cp)$")
    difficulty: str = Field(..., pattern=r"^(easy|medium|hard)$")
    rating: int = Field(default=800, ge=100, le=3500)
    description: str
    input_format: str
    output_format: str
    constraints: Optional[str] = None
    method_name: Optional[str] = None
    parameters: Optional[list[ProblemParameter]] = None
    return_type: Optional[str] = None
    time_limit_ms: int = Field(default=2000, ge=500, le=10000)
    memory_limit_mb: int = Field(default=256, ge=32, le=512)
    is_active: bool = True
    generator: Optional[GeneratorConfig] = None

    @model_validator(mode="after")
    def validate_signature(self) -> ProblemPackageMeta:
        has_method = bool(self.method_name)
        has_params = bool(self.parameters)
        has_return = bool(self.return_type)

        if has_method or has_params or has_return:
            if not (has_method and has_params and has_return):
                raise ValueError(
                    "LeetCode-style problems require method_name, parameters, and return_type"
                )
        return self

    def to_problem_kwargs(self) -> dict:
        return {
            "description": self.description,
            "difficulty": self.difficulty,
            "input_format": self.input_format,
            "output_format": self.output_format,
            "constraints": self.constraints,
            "problem_type": self.problem_type,
            "rating": self.rating,
            "time_limit_ms": self.time_limit_ms,
            "memory_limit_mb": self.memory_limit_mb,
            "method_name": self.method_name,
            "parameters": (
                [p.model_dump() for p in self.parameters] if self.parameters else None
            ),
            "return_type": self.return_type,
            "is_active": self.is_active,
        }
