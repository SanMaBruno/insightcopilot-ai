from __future__ import annotations

from src.application.services.executive_summary_context_builder import (
    build_system_prompt,
    build_user_prompt,
)
from src.domain.entities.dataset_insight import DatasetInsightReport, Insight
from src.domain.entities.dataset_profile import ColumnProfile, DatasetProfile


class TestBuildSystemPrompt:

    def test_includes_audience(self) -> None:
        result = build_system_prompt("directivos", "ejecutivo", 3)

        assert "directivos" in result

    def test_includes_tone(self) -> None:
        result = build_system_prompt("directivos", "ejecutivo", 3)

        assert "ejecutivo" in result

    def test_includes_max_paragraphs(self) -> None:
        result = build_system_prompt("directivos", "ejecutivo", 5)

        assert "5" in result

    def test_includes_no_hallucination_guardrail(self) -> None:
        result = build_system_prompt("directivos", "ejecutivo", 3)

        assert "ÚNICAMENTE" in result

    def test_includes_spanish_instruction(self) -> None:
        result = build_system_prompt("directivos", "ejecutivo", 3)

        assert "español" in result


class TestBuildUserPrompt:

    def _sample_profile(self) -> DatasetProfile:
        return DatasetProfile(
            dataset_id="ds-1",
            row_count=100,
            column_count=2,
            columns=[
                ColumnProfile(name="edad", dtype="int64", null_count=5, unique_count=50),
                ColumnProfile(name="nombre", dtype="object", null_count=0, unique_count=80),
            ],
        )

    def _sample_report(self) -> DatasetInsightReport:
        return DatasetInsightReport(
            dataset_id="ds-1",
            summary="100 filas y 2 columnas",
            insights=[
                Insight(category="calidad", message="5 nulos en edad"),
            ],
            warnings=["Dataset con pocos registros"],
        )

    def test_includes_dataset_name(self) -> None:
        result = build_user_prompt("ventas", self._sample_profile(), self._sample_report())

        assert "ventas" in result

    def test_includes_row_count(self) -> None:
        result = build_user_prompt("ventas", self._sample_profile(), self._sample_report())

        assert "100" in result

    def test_includes_column_details(self) -> None:
        result = build_user_prompt("ventas", self._sample_profile(), self._sample_report())

        assert "edad" in result
        assert "int64" in result
        assert "nombre" in result

    def test_includes_insights(self) -> None:
        result = build_user_prompt("ventas", self._sample_profile(), self._sample_report())

        assert "5 nulos en edad" in result

    def test_includes_warnings(self) -> None:
        result = build_user_prompt("ventas", self._sample_profile(), self._sample_report())

        assert "Dataset con pocos registros" in result

    def test_excludes_insights_section_when_empty(self) -> None:
        report = DatasetInsightReport(
            dataset_id="ds-1", summary="ok", insights=[], warnings=[],
        )
        result = build_user_prompt("ventas", self._sample_profile(), report)

        assert "Insights detectados" not in result
        assert "Advertencias" not in result
