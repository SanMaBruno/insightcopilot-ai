from __future__ import annotations

from src.domain.entities.dataset_insight import DatasetInsightReport, Insight
from src.domain.entities.dataset_profile import DatasetProfile
from src.domain.value_objects.column_profile import ColumnProfile

_NUMERIC_PREFIXES = ("int", "float")


def _is_numeric(col: ColumnProfile) -> bool:
    return col.dtype.startswith(_NUMERIC_PREFIXES)


def _build_summary(profile: DatasetProfile, numeric: int, categorical: int) -> str:
    return (
        f"Dataset con {profile.row_count} filas y {profile.column_count} columnas "
        f"({numeric} numéricas, {categorical} categóricas)."
    )


def _detect_insights(profile: DatasetProfile) -> list[Insight]:
    insights: list[Insight] = []

    numeric = [c for c in profile.columns if _is_numeric(c)]
    categorical = [c for c in profile.columns if not _is_numeric(c)]

    if numeric:
        names = ", ".join(c.name for c in numeric)
        insights.append(Insight("tipos", f"Columnas numéricas: {names}"))

    if categorical:
        names = ", ".join(c.name for c in categorical)
        insights.append(Insight("tipos", f"Columnas categóricas: {names}"))

    high_null = [
        c for c in profile.columns
        if profile.row_count > 0 and c.null_count > profile.row_count * 0.5
    ]
    if high_null:
        names = ", ".join(f"{c.name} ({c.null_count}/{profile.row_count})" for c in high_null)
        insights.append(Insight("nulos", f"Columnas con más del 50% de nulos: {names}"))

    constant = [c for c in profile.columns if c.unique_count <= 1 and c.null_count == 0]
    if constant:
        names = ", ".join(c.name for c in constant)
        insights.append(Insight("variabilidad", f"Columnas con un solo valor único: {names}"))

    return insights


def _detect_warnings(profile: DatasetProfile) -> list[str]:
    warnings: list[str] = []

    if profile.row_count == 0:
        warnings.append("El dataset está vacío (0 filas).")

    empty_cols = [c for c in profile.columns if c.null_count == profile.row_count]
    if empty_cols:
        names = ", ".join(c.name for c in empty_cols)
        warnings.append(f"Columnas completamente vacías: {names}")

    return warnings


def generate_insights(profile: DatasetProfile) -> DatasetInsightReport:
    numeric_count = sum(1 for c in profile.columns if _is_numeric(c))
    categorical_count = profile.column_count - numeric_count

    return DatasetInsightReport(
        dataset_id=profile.dataset_id,
        summary=_build_summary(profile, numeric_count, categorical_count),
        insights=_detect_insights(profile),
        warnings=_detect_warnings(profile),
    )
