from __future__ import annotations

from pydantic import BaseModel


class ColumnProfileResponse(BaseModel):
    name: str
    dtype: str
    null_count: int
    unique_count: int


class DatasetProfileResponse(BaseModel):
    dataset_id: str
    row_count: int
    column_count: int
    columns: list[ColumnProfileResponse]
