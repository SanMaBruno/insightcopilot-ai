from __future__ import annotations

from dataclasses import dataclass

from src.domain.value_objects.column_profile import ColumnProfile


@dataclass
class DatasetProfile:
    dataset_id: str
    row_count: int
    column_count: int
    columns: list[ColumnProfile]
