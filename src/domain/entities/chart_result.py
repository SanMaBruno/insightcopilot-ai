from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ChartResult:
    chart_type: str
    title: str
    columns: list[str]
    image_base64: str


@dataclass
class DatasetVisualization:
    dataset_id: str
    charts: list[ChartResult]
