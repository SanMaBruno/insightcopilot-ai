from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class QueryIntent(Enum):
    SUMMARY = "resumen"
    NULLS = "nulos"
    NUMERIC_COLUMNS = "columnas_numericas"
    CATEGORICAL_COLUMNS = "columnas_categoricas"
    WARNINGS = "advertencias"
    UNKNOWN = "desconocida"


@dataclass(frozen=True)
class AnalyticalQuery:
    dataset_id: str
    question: str


@dataclass
class AnalyticalAnswer:
    dataset_id: str
    intent: str
    question: str
    answer: str
    supporting_data: list[str] = field(default_factory=list)
