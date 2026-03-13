from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ExecutiveSummary:
    dataset_id: str
    audience: str
    tone: str
    content: str
