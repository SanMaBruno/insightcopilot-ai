from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class ChartSeriesResponse(BaseModel):
    name: str
    data: list[float]
    color: Optional[str] = None


class InteractiveChartSpecResponse(BaseModel):
    chart_kind: str
    subtitle: str = ""
    categories: list[str]
    series: list[ChartSeriesResponse]
    x_axis_label: str = ""
    y_axis_label: str = ""
    tooltip_suffix: str = ""
    source_label: str = ""


class ChartResultResponse(BaseModel):
    chart_type: str
    title: str
    columns: list[str]
    image_base64: str
    interactive_spec: Optional[InteractiveChartSpecResponse] = None


class DatasetVisualizationResponse(BaseModel):
    dataset_id: str
    charts: list[ChartResultResponse]
