from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ColumnRole(str, Enum):
    EMPTY = "empty"
    CONSTANT = "constant"
    HIGH_NULL = "high_null"
    IDENTIFIER = "identifier"
    NOISE = "noise"
    DATE_CANDIDATE = "date_candidate"
    LOW_VARIANCE = "low_variance"
    VALUABLE_NUMERIC = "valuable_numeric"
    VALUABLE_CATEGORICAL = "valuable_categorical"


@dataclass(frozen=True)
class ColumnClassification:
    column_name: str
    dtype: str
    role: ColumnRole
    null_ratio: float
    unique_ratio: float
    reason: str
    secondary_flags: tuple[str, ...] = ()
