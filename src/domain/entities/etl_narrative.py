from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4

from src.domain.value_objects.etl_narrative_sections import EtlNarrativeSections


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class EtlNarrative:
    dataset_id: str
    etl_run_id: str
    sections: EtlNarrativeSections
    execution_mode: str
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=_now_utc)
