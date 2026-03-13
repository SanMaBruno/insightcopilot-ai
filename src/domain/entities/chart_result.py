from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ChartSeries:
    name: str
    data: list[float]
    color: str | None = None


@dataclass(frozen=True)
class InteractiveChartSpec:
    chart_kind: str
    categories: list[str]
    series: list[ChartSeries]
    subtitle: str = ""
    x_axis_label: str = ""
    y_axis_label: str = ""
    tooltip_suffix: str = ""
    source_label: str = ""


@dataclass(frozen=True)
class ChartResult:
    chart_type: str
    title: str
    columns: list[str]
    image_base64: str
    interactive_spec: InteractiveChartSpec | None = None


@dataclass
class DatasetVisualization:
    dataset_id: str
    charts: list[ChartResult]
