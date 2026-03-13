from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Insight:
    category: str
    message: str


@dataclass
class DatasetInsightReport:
    dataset_id: str
    summary: str
    insights: list[Insight]
    warnings: list[str]
