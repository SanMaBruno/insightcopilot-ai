from __future__ import annotations

from pydantic import BaseModel, Field


class RagQueryRequest(BaseModel):
    question: str
    top_k: int = Field(default=5, ge=1, le=20)


class DocumentChunkResponse(BaseModel):
    source: str
    content: str
    chunk_index: int


class RagQueryResponse(BaseModel):
    dataset_id: str
    question: str
    answer: str
    sources: list[DocumentChunkResponse]
