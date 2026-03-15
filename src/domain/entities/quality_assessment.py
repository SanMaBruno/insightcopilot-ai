from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4

from src.domain.value_objects.column_classification import ColumnClassification
from src.domain.value_objects.quality_score import QualityScore


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class QualityAssessment:
    dataset_id: str
    etl_run_id: str
    score: QualityScore
    column_assessments: list[ColumnClassification]
    row_count: int
    column_count: int
    duplicate_row_count: int
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=_now_utc)
