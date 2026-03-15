from __future__ import annotations

from src.domain.value_objects.column_classification import (
    ColumnClassification,
    ColumnRole,
)
from src.domain.value_objects.transformation_step import TransformAction, TransformationStep

_CONSERVATIVE_MAP: dict[ColumnRole, TransformAction] = {
    ColumnRole.EMPTY: TransformAction.DROP_COLUMN,
    ColumnRole.CONSTANT: TransformAction.DROP_COLUMN,
    ColumnRole.HIGH_NULL: TransformAction.KEEP,
    ColumnRole.IDENTIFIER: TransformAction.KEEP,
    ColumnRole.NOISE: TransformAction.KEEP,
    ColumnRole.LOW_VARIANCE: TransformAction.KEEP,
    ColumnRole.DATE_CANDIDATE: TransformAction.CAST_TYPE,
    ColumnRole.VALUABLE_NUMERIC: TransformAction.FILL_NULLS_MEDIAN,
    ColumnRole.VALUABLE_CATEGORICAL: TransformAction.FILL_NULLS_MODE,
}

_AGGRESSIVE_MAP: dict[ColumnRole, TransformAction] = {
    ColumnRole.EMPTY: TransformAction.DROP_COLUMN,
    ColumnRole.CONSTANT: TransformAction.DROP_COLUMN,
    ColumnRole.HIGH_NULL: TransformAction.DROP_COLUMN,
    ColumnRole.IDENTIFIER: TransformAction.DROP_COLUMN,
    ColumnRole.NOISE: TransformAction.DROP_COLUMN,
    ColumnRole.LOW_VARIANCE: TransformAction.DROP_COLUMN,
    ColumnRole.DATE_CANDIDATE: TransformAction.CAST_TYPE,
    ColumnRole.VALUABLE_NUMERIC: TransformAction.FILL_NULLS_MEDIAN,
    ColumnRole.VALUABLE_CATEGORICAL: TransformAction.FILL_NULLS_UNKNOWN,
}


def generate_plan_steps(
    classifications: list[ColumnClassification],
    duplicate_row_count: int,
    strategy: str = "conservative",
) -> list[TransformationStep]:
    action_map = _AGGRESSIVE_MAP if strategy == "aggressive" else _CONSERVATIVE_MAP
    steps: list[TransformationStep] = []
    priority = 0

    # Step 0: normalize column names
    steps.append(
        TransformationStep(
            column_name=None,
            action=TransformAction.NORMALIZE_NAMES,
            params={},
            reason="Normalizar nombres de columnas (minúsculas, sin espacios extra)",
            priority=(priority := priority + 1),
        )
    )

    for col in classifications:
        action = action_map[col.role]

        if action == TransformAction.KEEP and col.null_ratio == 0:
            continue

        if action == TransformAction.KEEP:
            steps.append(
                TransformationStep(
                    column_name=col.column_name,
                    action=TransformAction.KEEP,
                    params={},
                    reason=f"Se conserva con advertencia — {col.reason}",
                    priority=(priority := priority + 1),
                )
            )
            continue

        if action in (TransformAction.FILL_NULLS_MEDIAN, TransformAction.FILL_NULLS_MODE, TransformAction.FILL_NULLS_UNKNOWN):
            if col.null_ratio == 0:
                continue
            reason = _fill_reason(col, action)
        elif action == TransformAction.DROP_COLUMN:
            reason = f"Eliminar — {col.reason}"
        elif action == TransformAction.CAST_TYPE:
            reason = f"Convertir a datetime — {col.reason}"
        else:
            reason = col.reason

        params: dict[str, str] = {}
        if action == TransformAction.CAST_TYPE:
            params["target_type"] = "datetime64"
        if action == TransformAction.FILL_NULLS_UNKNOWN:
            params["fill_value"] = "Desconocido"

        steps.append(
            TransformationStep(
                column_name=col.column_name,
                action=action,
                params=params,
                reason=reason,
                priority=(priority := priority + 1),
            )
        )

    # Strip whitespace for all categorical columns
    for col in classifications:
        if col.dtype == "object" and col.role not in (ColumnRole.EMPTY, ColumnRole.CONSTANT):
            if action_map[col.role] != TransformAction.DROP_COLUMN:
                steps.append(
                    TransformationStep(
                        column_name=col.column_name,
                        action=TransformAction.STRIP_WHITESPACE,
                        params={},
                        reason="Limpiar espacios en blanco al inicio y final",
                        priority=(priority := priority + 1),
                    )
                )

    # Remove duplicates if detected
    if duplicate_row_count > 0:
        if strategy == "aggressive":
            steps.append(
                TransformationStep(
                    column_name=None,
                    action=TransformAction.REMOVE_DUPLICATES,
                    params={},
                    reason=f"Eliminar {duplicate_row_count} fila(s) duplicada(s)",
                    priority=(priority := priority + 1),
                )
            )
        else:
            steps.append(
                TransformationStep(
                    column_name=None,
                    action=TransformAction.KEEP,
                    params={},
                    reason=f"Se detectaron {duplicate_row_count} fila(s) duplicada(s) — se conservan en modo conservador",
                    priority=(priority := priority + 1),
                )
            )

    return steps


def _fill_reason(col: ColumnClassification, action: TransformAction) -> str:
    pct = f"{col.null_ratio:.0%}"
    if action == TransformAction.FILL_NULLS_MEDIAN:
        return f"Rellenar nulos con mediana ({pct} nulos)"
    if action == TransformAction.FILL_NULLS_MODE:
        return f"Rellenar nulos con moda ({pct} nulos)"
    return f"Rellenar nulos con 'Desconocido' ({pct} nulos)"
