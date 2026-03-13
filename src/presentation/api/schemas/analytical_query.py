from __future__ import annotations

from pydantic import BaseModel


class AnalyticalQueryRequest(BaseModel):
    question: str


class AnalyticalAnswerResponse(BaseModel):
    dataset_id: str
    intent: str
    question: str
    answer: str
    supporting_data: list[str]
