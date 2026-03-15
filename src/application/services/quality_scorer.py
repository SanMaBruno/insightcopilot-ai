from __future__ import annotations

from src.domain.repositories.dataset_loader import RawDatasetData
from src.domain.value_objects.column_classification import (
    ColumnClassification,
    ColumnRole,
)
from src.domain.value_objects.quality_score import QualityScore

_INVALID_ROLES = frozenset({
    ColumnRole.EMPTY,
    ColumnRole.CONSTANT,
    ColumnRole.NOISE,
})


def compute_quality_score(
    raw: RawDatasetData,
    classifications: list[ColumnClassification],
    duplicate_row_count: int,
) -> QualityScore:
    total_cells = raw.row_count * len(raw.columns) if raw.columns else 1
    total_nulls = sum(raw.null_counts.values())

    completeness = 1.0 - (total_nulls / total_cells) if total_cells > 0 else 1.0

    type_consistent = sum(
        1 for c in classifications
        if c.role not in (ColumnRole.DATE_CANDIDATE,)
    )
    consistency = type_consistent / len(classifications) if classifications else 1.0

    uniqueness = (
        1.0 - (duplicate_row_count / raw.row_count)
        if raw.row_count > 0
        else 1.0
    )

    valid_cols = sum(1 for c in classifications if c.role not in _INVALID_ROLES)
    validity = valid_cols / len(classifications) if classifications else 1.0

    overall = round(
        0.35 * completeness + 0.20 * consistency + 0.20 * uniqueness + 0.25 * validity,
        4,
    )

    return QualityScore(
        completeness=round(completeness, 4),
        consistency=round(consistency, 4),
        uniqueness=round(uniqueness, 4),
        validity=round(validity, 4),
        overall=overall,
    )
