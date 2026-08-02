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


class ExampleSpec(BaseModel):
    """Optional LeetCode-style example overlay (merged with samples/ at sync)."""

    input: Optional[str] = None
    output: Optional[str] = None
    explanation: Optional[str] = None


class ImageSpec(BaseModel):
    """Diagram or illustration shown in the problem panel."""

    src: str = Field(..., min_length=1)
    alt: Optional[str] = None


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
    examples: Optional[list[ExampleSpec]] = None
    images: Optional[list[ImageSpec]] = None
    # Judge hint for Meta "return in any order" outputs: "outer" | "deep"
    unordered_output: Optional[str] = Field(
        default=None,
        pattern=r"^(outer|deep)$",
        description="JSON compare mode when answer order is free: outer=top-level only, deep=all levels",
    )

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
            "presentation": self.build_presentation(),
        }

    def build_presentation(self) -> dict | None:
        images = [img.model_dump() for img in self.images] if self.images else []
        examples = [ex.model_dump(exclude_none=True) for ex in self.examples] if self.examples else []
        if not images and not examples and not self.unordered_output:
            return None
        payload: dict = {}
        if examples:
            payload["examples"] = examples
        if images:
            payload["images"] = images
        if self.unordered_output:
            payload["unordered_output"] = self.unordered_output
        return payload
