from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class TransformAction(str, Enum):
    NORMALIZE_NAMES = "normalize_names"
    DROP_COLUMN = "drop_column"
    FILL_NULLS_MEDIAN = "fill_nulls_median"
    FILL_NULLS_MODE = "fill_nulls_mode"
    FILL_NULLS_UNKNOWN = "fill_nulls_unknown"
    CAST_TYPE = "cast_type"
    REMOVE_DUPLICATES = "remove_duplicates"
    STRIP_WHITESPACE = "strip_whitespace"
    KEEP = "keep"


@dataclass(frozen=True)
class TransformationStep:
    column_name: Optional[str]
    action: TransformAction
    params: dict[str, str]
    reason: str
    priority: int
