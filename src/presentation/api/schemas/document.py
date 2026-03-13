from __future__ import annotations

from pydantic import BaseModel, Field


class DocumentUploadResponse(BaseModel):
    source: str
    file_path: str


class DocumentIndexRequest(BaseModel):
    file_path: str
    chunk_size: int = Field(default=500, ge=100, le=2000)
    overlap: int = Field(default=50, ge=0, le=500)


class DocumentIndexResponse(BaseModel):
    source: str
    chunks_indexed: int
