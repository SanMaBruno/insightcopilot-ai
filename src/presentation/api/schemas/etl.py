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


# --- Phase 2: Execution ---


class ExecuteEtlRequest(BaseModel):
    etl_run_id: str
    quality_assessment_id: str
    strategy: str = "conservative"


class ExecutedStepResponse(BaseModel):
    action: str
    column_name: Optional[str]
    success: bool
    rows_before: int
    rows_after: int
    columns_before: int
    columns_after: int
    detail: str


class CuratedResultResponse(BaseModel):
    id: str
    dataset_id: str
    etl_run_id: str
    plan_id: str
    strategy: str
    status: str
    curated_file_path: str
    original_row_count: int
    curated_row_count: int
    original_column_count: int
    curated_column_count: int
    original_null_count: int
    curated_null_count: int
    executed_steps: list[ExecutedStepResponse]
    execution_time_ms: int
    execution_mode: str = "manual"
