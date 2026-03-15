from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4

from src.domain.value_objects.executed_step import ExecutedStep


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class CuratedResult:
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
    executed_steps: list[ExecutedStep]
    execution_time_ms: int
    execution_mode: str = "manual"
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=_now_utc)
