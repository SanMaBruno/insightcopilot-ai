from __future__ import annotations

from pydantic import BaseModel, Field


class ExecutiveSummaryRequest(BaseModel):
    audience: str = Field(default="equipo técnico", examples=["directivos", "equipo técnico"])
    tone: str = Field(default="profesional", examples=["profesional", "ejecutivo", "informal"])
    max_paragraphs: int = Field(default=3, ge=1, le=10)


class ExecutiveSummaryResponse(BaseModel):
    dataset_id: str
    audience: str
    tone: str
    content: str
