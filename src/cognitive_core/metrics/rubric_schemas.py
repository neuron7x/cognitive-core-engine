"""Pydantic schemas for UMAA+EPAUP rubrics."""
from __future__ import annotations
from typing import Dict, Any
from pydantic import BaseModel, Field


class JudgeSpec(BaseModel):
    model: str = Field(..., description="LLM model identifier")
    prompt: str = Field(..., description="Instruction for the judge model")


class MetricSpec(BaseModel):
    name: str
    weight: float = Field(1.0, ge=0)
    judge: JudgeSpec | None = None


class Rubric(BaseModel):
    version: int = 1
    metrics: list[MetricSpec]
    aggregation: str = Field("weighted_mean")


def load_rubric(data: Dict[str, Any]) -> Rubric:
    """Load a rubric from parsed YAML data."""
    return Rubric.model_validate(data)
