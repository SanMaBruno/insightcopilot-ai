from __future__ import annotations

import re

from src.domain.repositories.dataset_loader import RawDatasetData
from src.domain.value_objects.column_classification import (
    ColumnClassification,
    ColumnRole,
)

_NUMERIC_PREFIXES = ("int", "float")
_ID_NAME_PATTERN = re.compile(
    r"(^id$|_id$|^id_|^key$|_key$|^index$|_index$|^code$|_code$|^uuid|^pk$)",
    re.IGNORECASE,
)
_DATE_NAME_PATTERN = re.compile(
    r"(date|fecha|time|timestamp|created|updated|born|nacim)",
    re.IGNORECASE,
)


def _is_numeric(dtype: str) -> bool:
    return dtype.startswith(_NUMERIC_PREFIXES)


def classify_columns(raw: RawDatasetData) -> list[ColumnClassification]:
    results: list[ColumnClassification] = []

    for col in raw.columns:
        dtype = raw.dtypes[col]
        null_count = raw.null_counts[col]
        unique_count = raw.unique_counts[col]
        row_count = raw.row_count

        null_ratio = null_count / row_count if row_count > 0 else 0.0
        unique_ratio = unique_count / row_count if row_count > 0 else 0.0

        role, reason, flags = _classify_single(
            col, dtype, null_ratio, unique_ratio, null_count, unique_count, row_count,
        )

        results.append(
            ColumnClassification(
                column_name=col,
                dtype=dtype,
                role=role,
                null_ratio=round(null_ratio, 4),
                unique_ratio=round(unique_ratio, 4),
                reason=reason,
                secondary_flags=tuple(flags),
            )
        )

    return results


def _classify_single(
    name: str,
    dtype: str,
    null_ratio: float,
    unique_ratio: float,
    null_count: int,
    unique_count: int,
    row_count: int,
) -> tuple[ColumnRole, str, list[str]]:
    flags: list[str] = []

    # 1. EMPTY — 100% nulos
    if row_count > 0 and null_count == row_count:
        return ColumnRole.EMPTY, "Columna completamente vacía (0 valores presentes)", flags

    # 2. CONSTANT — un solo valor único, sin nulos
    if unique_count <= 1 and null_count == 0:
        return ColumnRole.CONSTANT, "Valor constante en todas las filas — sin información útil", flags

    # 3. HIGH_NULL — >50% nulos
    if null_ratio > 0.50:
        flags = _collect_secondary_flags(name, dtype, unique_ratio, row_count)
        pct = f"{null_ratio:.0%}"
        return ColumnRole.HIGH_NULL, f"{pct} de valores nulos — baja confiabilidad", flags

    # 4. IDENTIFIER — alta cardinalidad + patrón de nombre o secuencial
    if _is_identifier(name, dtype, unique_ratio, row_count):
        reason = f"Alta cardinalidad ({unique_ratio:.0%} únicos) + patrón de nombre '{name}' → probable identificador"
        return ColumnRole.IDENTIFIER, reason, flags

    # 5. NOISE — texto con cardinalidad excesiva
    if dtype == "object" and unique_ratio > 0.80 and row_count > 50:
        return ColumnRole.NOISE, f"Texto libre con alta cardinalidad ({unique_ratio:.0%} únicos) — probable ruido", flags

    # 6. DATE_CANDIDATE — nombre sugiere fecha + dtype object
    if dtype == "object" and _DATE_NAME_PATTERN.search(name):
        flags.append("parseable_as_date")
        return ColumnRole.DATE_CANDIDATE, f"Nombre '{name}' sugiere fecha, tipo actual: object", flags

    # 7. LOW_VARIANCE — muy pocos valores únicos, no constante
    if unique_count <= 2 and row_count > 10:
        return ColumnRole.LOW_VARIANCE, f"Solo {unique_count} valor(es) único(s) — variabilidad muy baja", flags

    # 8. VALUABLE
    if _is_numeric(dtype):
        flags = _collect_secondary_flags(name, dtype, unique_ratio, row_count)
        return ColumnRole.VALUABLE_NUMERIC, "Columna numérica con rango de valores adecuado", flags

    flags = _collect_secondary_flags(name, dtype, unique_ratio, row_count)
    return ColumnRole.VALUABLE_CATEGORICAL, "Columna categórica con diversidad aceptable", flags


def _is_identifier(name: str, dtype: str, unique_ratio: float, row_count: int) -> bool:
    if row_count < 10:
        return False
    has_id_name = bool(_ID_NAME_PATTERN.search(name))
    if dtype == "object" and unique_ratio > 0.90 and has_id_name:
        return True
    if _is_numeric(dtype) and unique_ratio > 0.95 and has_id_name:
        return True
    return False


def _collect_secondary_flags(
    name: str, dtype: str, unique_ratio: float, row_count: int,
) -> list[str]:
    flags: list[str] = []
    if _DATE_NAME_PATTERN.search(name) and dtype == "object":
        flags.append("possible_date")
    if _ID_NAME_PATTERN.search(name):
        flags.append("possible_id")
    if _is_numeric(dtype) and unique_ratio < 0.05 and row_count > 20:
        flags.append("low_cardinality_numeric")
    return flags
