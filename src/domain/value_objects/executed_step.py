from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from src.domain.value_objects.transformation_step import TransformAction


@dataclass(frozen=True)
class ExecutedStep:
    action: TransformAction
    column_name: Optional[str]
    success: bool
    rows_before: int
    rows_after: int
    columns_before: int
    columns_after: int
    detail: str
