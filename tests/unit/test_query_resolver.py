from __future__ import annotations

from src.application.services.query_resolver import build_answer, detect_intent
from src.domain.entities.analytical_query import QueryIntent
from src.domain.entities.dataset_insight import DatasetInsightReport, Insight
from src.domain.entities.dataset_profile import DatasetProfile
from src.domain.value_objects.column_profile import ColumnProfile


def _make_profile() -> DatasetProfile:
    return DatasetProfile(
        dataset_id="ds-1",
        row_count=100,
        column_count=3,
        columns=[
            ColumnProfile(name="age", dtype="int64", null_count=5, unique_count=50),
            ColumnProfile(name="name", dtype="object", null_count=0, unique_count=80),
            ColumnProfile(name="city", dtype="object", null_count=60, unique_count=10),
        ],
    )


def _make_report() -> DatasetInsightReport:
    return DatasetInsightReport(
        dataset_id="ds-1",
        summary="Dataset con 100 filas y 3 columnas (1 numéricas, 2 categóricas).",
        insights=[
            Insight("tipos", "Columnas numéricas: age"),
            Insight("tipos", "Columnas categóricas: name, city"),
        ],
        warnings=["Columnas completamente vacías: city"],
    )


class TestDetectIntent:

    def test_detects_nulls(self) -> None:
        assert detect_intent("¿Qué columnas tienen nulos?") == QueryIntent.NULLS

    def test_detects_nulls_english(self) -> None:
        assert detect_intent("show me null columns") == QueryIntent.NULLS

    def test_detects_numeric(self) -> None:
        assert detect_intent("¿Cuáles son las columnas numéricas?") == QueryIntent.NUMERIC_COLUMNS

    def test_detects_categorical(self) -> None:
        assert detect_intent("columnas categóricas del dataset") == QueryIntent.CATEGORICAL_COLUMNS

    def test_detects_warnings(self) -> None:
        assert detect_intent("¿Hay alguna advertencia?") == QueryIntent.WARNINGS

    def test_detects_summary(self) -> None:
        assert detect_intent("Dame un resumen general") == QueryIntent.SUMMARY

    def test_returns_unknown_for_unrecognized(self) -> None:
        assert detect_intent("abc xyz 123") == QueryIntent.UNKNOWN


class TestBuildAnswer:

    def setup_method(self) -> None:
        self.profile = _make_profile()
        self.report = _make_report()

    def test_summary_includes_row_count(self) -> None:
        answer = build_answer("resumen", QueryIntent.SUMMARY, self.profile, self.report)

        assert answer.intent == "resumen"
        assert "100 filas" in answer.answer
        assert any("Filas: 100" in d for d in answer.supporting_data)

    def test_nulls_returns_ranked_columns(self) -> None:
        answer = build_answer("nulos", QueryIntent.NULLS, self.profile, self.report)

        assert answer.intent == "nulos"
        assert "2 columna(s)" in answer.answer
        assert answer.supporting_data[0].startswith("city")  # most nulls first

    def test_numeric_lists_columns(self) -> None:
        answer = build_answer("numéricas", QueryIntent.NUMERIC_COLUMNS, self.profile, self.report)

        assert answer.intent == "columnas_numericas"
        assert "1 columna(s)" in answer.answer
        assert any("age" in d for d in answer.supporting_data)

    def test_categorical_lists_columns(self) -> None:
        answer = build_answer(
            "categóricas", QueryIntent.CATEGORICAL_COLUMNS, self.profile, self.report
        )

        assert answer.intent == "columnas_categoricas"
        assert "2 columna(s)" in answer.answer

    def test_warnings_lists_them(self) -> None:
        answer = build_answer("advertencias", QueryIntent.WARNINGS, self.profile, self.report)

        assert answer.intent == "advertencias"
        assert "1 advertencia(s)" in answer.answer
        assert len(answer.supporting_data) == 1

    def test_unknown_provides_help(self) -> None:
        answer = build_answer("xyz", QueryIntent.UNKNOWN, self.profile, self.report)

        assert answer.intent == "desconocida"
        assert "No pude entender" in answer.answer

    def test_question_is_preserved(self) -> None:
        answer = build_answer(
            "¿Cuántos nulos hay?", QueryIntent.NULLS, self.profile, self.report
        )

        assert answer.question == "¿Cuántos nulos hay?"
