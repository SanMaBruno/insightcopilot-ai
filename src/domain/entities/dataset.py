from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class Dataset:
    name: str
    file_path: str
    source_type: str
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=_now_utc)
