from __future__ import annotations

from pydantic import BaseModel


class InsightResponse(BaseModel):
    category: str
    message: str


class DatasetInsightReportResponse(BaseModel):
    dataset_id: str
    summary: str
    insights: list[InsightResponse]
    warnings: list[str]
