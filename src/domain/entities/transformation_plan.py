from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4

from src.domain.value_objects.transformation_step import TransformationStep


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


class PlanStatus(str, Enum):
    PROPOSED = "proposed"
    APPROVED = "approved"
    EXECUTED = "executed"


@dataclass
class TransformationPlan:
    dataset_id: str
    etl_run_id: str
    quality_assessment_id: str
    strategy: str
    steps: list[TransformationStep]
    status: PlanStatus = PlanStatus.PROPOSED
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=_now_utc)
