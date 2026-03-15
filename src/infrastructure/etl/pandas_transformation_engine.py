from __future__ import annotations

import re

import pandas as pd

from src.domain.repositories.transformation_engine import (
    TransformationEngine,
    TransformationOutput,
)
from src.domain.value_objects.executed_step import ExecutedStep
from src.domain.value_objects.transformation_step import TransformAction, TransformationStep


class PandasTransformationEngine(TransformationEngine):

    def execute(
        self, file_path: str, steps: list[TransformationStep],
    ) -> TransformationOutput:
        df = pd.read_csv(file_path)
        executed: list[ExecutedStep] = []

        sorted_steps = sorted(steps, key=lambda s: s.priority)

        for step in sorted_steps:
            rows_before = len(df)
            cols_before = len(df.columns)

            handler = _HANDLERS.get(step.action)
            if handler is None:
                executed.append(
                    ExecutedStep(
                        action=step.action,
                        column_name=step.column_name,
                        success=False,
                        rows_before=rows_before,
                        rows_after=rows_before,
                        columns_before=cols_before,
                        columns_after=cols_before,
                        detail=f"Acción no soportada: {step.action.value}",
                    ),
                )
                continue

            df, detail, success = handler(df, step)

            executed.append(
                ExecutedStep(
                    action=step.action,
                    column_name=step.column_name,
                    success=success,
                    rows_before=rows_before,
                    rows_after=len(df),
                    columns_before=cols_before,
                    columns_after=len(df.columns),
                    detail=detail,
                ),
            )

        csv_bytes = df.to_csv(index=False).encode("utf-8")
        null_count = int(df.isnull().sum().sum())

        return TransformationOutput(
            csv_bytes=csv_bytes,
            executed_steps=executed,
            row_count=len(df),
            column_count=len(df.columns),
            null_count=null_count,
        )


# ---------------------------------------------------------------------------
# Handlers — each returns (df, detail, success)
# ---------------------------------------------------------------------------

_StepResult = tuple[pd.DataFrame, str, bool]


def _normalize_names(df: pd.DataFrame, _step: TransformationStep) -> _StepResult:
    original = list(df.columns)
    df.columns = [re.sub(r"\s+", "_", c.strip().lower()) for c in df.columns]
    changed = sum(1 for a, b in zip(original, df.columns) if a != b)
    return df, f"{changed} nombre(s) de columna normalizado(s)", True


def _drop_column(df: pd.DataFrame, step: TransformationStep) -> _StepResult:
    col = step.column_name
    if col is None or col not in df.columns:
        return df, f"Columna '{col}' no encontrada — omitida", False
    df = df.drop(columns=[col])
    return df, f"Columna '{col}' eliminada", True


def _remove_duplicates(df: pd.DataFrame, _step: TransformationStep) -> _StepResult:
    before = len(df)
    df = df.drop_duplicates()
    removed = before - len(df)
    return df, f"{removed} fila(s) duplicada(s) eliminada(s)", True


def _strip_whitespace(df: pd.DataFrame, step: TransformationStep) -> _StepResult:
    col = step.column_name
    if col is None or col not in df.columns:
        return df, f"Columna '{col}' no encontrada — omitida", False
    if df[col].dtype == object:
        df[col] = df[col].str.strip()
        return df, f"Espacios en blanco limpiados en '{col}'", True
    return df, f"Columna '{col}' no es texto — omitida", False


def _cast_type(df: pd.DataFrame, step: TransformationStep) -> _StepResult:
    col = step.column_name
    target = step.params.get("target_type", "")
    if col is None or col not in df.columns:
        return df, f"Columna '{col}' no encontrada — omitida", False
    if target == "datetime64":
        df[col] = pd.to_datetime(df[col], errors="coerce")
        return df, f"Columna '{col}' convertida a datetime", True
    return df, f"Tipo destino '{target}' no soportado — omitida", False


def _fill_nulls_median(df: pd.DataFrame, step: TransformationStep) -> _StepResult:
    col = step.column_name
    if col is None or col not in df.columns:
        return df, f"Columna '{col}' no encontrada — omitida", False
    nulls_before = int(df[col].isnull().sum())
    if nulls_before == 0:
        return df, f"Sin nulos en '{col}' — sin cambios", False
    median_val = df[col].median()
    df[col] = df[col].fillna(median_val)
    return df, f"{nulls_before} nulo(s) en '{col}' rellenados con mediana ({median_val})", True


def _fill_nulls_mode(df: pd.DataFrame, step: TransformationStep) -> _StepResult:
    col = step.column_name
    if col is None or col not in df.columns:
        return df, f"Columna '{col}' no encontrada — omitida", False
    nulls_before = int(df[col].isnull().sum())
    if nulls_before == 0:
        return df, f"Sin nulos en '{col}' — sin cambios", False
    mode_series = df[col].mode()
    if mode_series.empty:
        return df, f"No se pudo calcular moda para '{col}' — omitida", False
    mode_val = mode_series.iloc[0]
    df[col] = df[col].fillna(mode_val)
    return df, f"{nulls_before} nulo(s) en '{col}' rellenados con moda ({mode_val})", True


def _fill_nulls_unknown(df: pd.DataFrame, step: TransformationStep) -> _StepResult:
    col = step.column_name
    fill_value = step.params.get("fill_value", "Desconocido")
    if col is None or col not in df.columns:
        return df, f"Columna '{col}' no encontrada — omitida", False
    nulls_before = int(df[col].isnull().sum())
    if nulls_before == 0:
        return df, f"Sin nulos en '{col}' — sin cambios", False
    df[col] = df[col].fillna(fill_value)
    return df, f"{nulls_before} nulo(s) en '{col}' rellenados con '{fill_value}'", True


def _keep(df: pd.DataFrame, step: TransformationStep) -> _StepResult:
    target = step.column_name if step.column_name else "filas"
    return df, f"'{target}' conservado sin cambios", False


_HANDLERS: dict[
    TransformAction,
    "type[object]",  # Callable[[pd.DataFrame, TransformationStep], _StepResult]
] = {
    TransformAction.NORMALIZE_NAMES: _normalize_names,
    TransformAction.DROP_COLUMN: _drop_column,
    TransformAction.REMOVE_DUPLICATES: _remove_duplicates,
    TransformAction.STRIP_WHITESPACE: _strip_whitespace,
    TransformAction.CAST_TYPE: _cast_type,
    TransformAction.FILL_NULLS_MEDIAN: _fill_nulls_median,
    TransformAction.FILL_NULLS_MODE: _fill_nulls_mode,
    TransformAction.FILL_NULLS_UNKNOWN: _fill_nulls_unknown,
    TransformAction.KEEP: _keep,
}
