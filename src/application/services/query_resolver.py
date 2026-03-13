from __future__ import annotations

from src.domain.entities.analytical_query import AnalyticalAnswer, QueryIntent
from src.domain.entities.dataset_insight import DatasetInsightReport
from src.domain.entities.dataset_profile import DatasetProfile
from src.domain.value_objects.column_profile import ColumnProfile

_NUMERIC_PREFIXES = ("int", "float")

_INTENT_KEYWORDS: list[tuple[QueryIntent, list[str]]] = [
    (QueryIntent.NULLS, ["nulo", "null", "faltante", "missing", "vacío", "vacio"]),
    (QueryIntent.NUMERIC_COLUMNS, ["numéric", "numeric", "número", "numero", "int", "float"]),
    (QueryIntent.CATEGORICAL_COLUMNS, ["categóric", "categoric", "texto", "text", "object"]),
    (QueryIntent.WARNINGS, ["warning", "advertencia", "problema", "alerta", "error"]),
    (QueryIntent.SUMMARY, ["resumen", "summary", "general", "describe", "describir", "overview"]),
]


def detect_intent(question: str) -> QueryIntent:
    q = question.lower()
    for intent, keywords in _INTENT_KEYWORDS:
        if any(kw in q for kw in keywords):
            return intent
    return QueryIntent.UNKNOWN


def _is_numeric(col: ColumnProfile) -> bool:
    return col.dtype.startswith(_NUMERIC_PREFIXES)


def _answer_summary(
    profile: DatasetProfile, report: DatasetInsightReport
) -> AnalyticalAnswer:
    details = [f"Filas: {profile.row_count}", f"Columnas: {profile.column_count}"]
    for col in profile.columns:
        details.append(f"  - {col.name} ({col.dtype}): {col.null_count} nulos")
    return AnalyticalAnswer(
        dataset_id=profile.dataset_id,
        intent=QueryIntent.SUMMARY.value,
        question="",
        answer=report.summary,
        supporting_data=details,
    )


def _answer_nulls(profile: DatasetProfile) -> AnalyticalAnswer:
    ranked = sorted(profile.columns, key=lambda c: c.null_count, reverse=True)
    lines = [f"{c.name}: {c.null_count} nulos" for c in ranked if c.null_count > 0]
    if not lines:
        answer = "No se encontraron valores nulos en el dataset."
    else:
        answer = f"Se encontraron {len(lines)} columna(s) con nulos."
    return AnalyticalAnswer(
        dataset_id=profile.dataset_id,
        intent=QueryIntent.NULLS.value,
        question="",
        answer=answer,
        supporting_data=lines,
    )


def _answer_numeric(profile: DatasetProfile) -> AnalyticalAnswer:
    cols = [c for c in profile.columns if _is_numeric(c)]
    names = [c.name for c in cols]
    answer = (
        f"El dataset tiene {len(cols)} columna(s) numérica(s)."
        if cols
        else "No hay columnas numéricas en el dataset."
    )
    return AnalyticalAnswer(
        dataset_id=profile.dataset_id,
        intent=QueryIntent.NUMERIC_COLUMNS.value,
        question="",
        answer=answer,
        supporting_data=[f"{c.name} ({c.dtype})" for c in cols] if names else [],
    )


def _answer_categorical(profile: DatasetProfile) -> AnalyticalAnswer:
    cols = [c for c in profile.columns if not _is_numeric(c)]
    answer = (
        f"El dataset tiene {len(cols)} columna(s) categórica(s)."
        if cols
        else "No hay columnas categóricas en el dataset."
    )
    return AnalyticalAnswer(
        dataset_id=profile.dataset_id,
        intent=QueryIntent.CATEGORICAL_COLUMNS.value,
        question="",
        answer=answer,
        supporting_data=[f"{c.name} ({c.dtype})" for c in cols],
    )


def _answer_warnings(report: DatasetInsightReport) -> AnalyticalAnswer:
    if report.warnings:
        answer = f"Se detectaron {len(report.warnings)} advertencia(s)."
    else:
        answer = "No se detectaron advertencias en el dataset."
    return AnalyticalAnswer(
        dataset_id=report.dataset_id,
        intent=QueryIntent.WARNINGS.value,
        question="",
        answer=answer,
        supporting_data=list(report.warnings),
    )


def _answer_unknown(dataset_id: str) -> AnalyticalAnswer:
    return AnalyticalAnswer(
        dataset_id=dataset_id,
        intent=QueryIntent.UNKNOWN.value,
        question="",
        answer="No pude entender la consulta. Intenta preguntar sobre: "
        "resumen, nulos, columnas numéricas, columnas categóricas o advertencias.",
        supporting_data=[],
    )


_HANDLERS = {
    QueryIntent.SUMMARY: lambda p, r: _answer_summary(p, r),
    QueryIntent.NULLS: lambda p, _r: _answer_nulls(p),
    QueryIntent.NUMERIC_COLUMNS: lambda p, _r: _answer_numeric(p),
    QueryIntent.CATEGORICAL_COLUMNS: lambda p, _r: _answer_categorical(p),
    QueryIntent.WARNINGS: lambda _p, r: _answer_warnings(r),
}


def build_answer(
    question: str,
    intent: QueryIntent,
    profile: DatasetProfile,
    report: DatasetInsightReport,
) -> AnalyticalAnswer:
    handler = _HANDLERS.get(intent)
    answer = _answer_unknown(profile.dataset_id) if handler is None else handler(profile, report)
    answer.question = question
    return answer
