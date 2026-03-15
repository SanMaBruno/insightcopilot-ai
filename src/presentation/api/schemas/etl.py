from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class ColumnClassificationResponse(BaseModel):
    column_name: str
    dtype: str
    role: str
    null_ratio: float
    unique_ratio: float
    reason: str
    secondary_flags: list[str]


class QualityScoreResponse(BaseModel):
    completeness: float
    consistency: float
    uniqueness: float
    validity: float
    overall: float


class QualityAssessmentResponse(BaseModel):
    id: str
    dataset_id: str
    etl_run_id: str
    score: QualityScoreResponse
    column_assessments: list[ColumnClassificationResponse]
    row_count: int
    column_count: int
    duplicate_row_count: int


class TransformationStepResponse(BaseModel):
    column_name: Optional[str]
    action: str
    params: dict[str, str]
    reason: str
    priority: int


class TransformPlanRequest(BaseModel):
    etl_run_id: str
    quality_assessment_id: str
    strategy: str = "conservative"


class TransformationPlanResponse(BaseModel):
    id: str
    dataset_id: str
    etl_run_id: str
    quality_assessment_id: str
    strategy: str
    status: str
    steps: list[TransformationStepResponse]
