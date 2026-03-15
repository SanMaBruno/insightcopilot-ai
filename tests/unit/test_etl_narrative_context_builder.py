from __future__ import annotations

from src.application.services.etl_narrative_context_builder import (
    build_system_prompt,
    build_user_prompt,
)
from src.domain.entities.curated_result import CuratedResult
from src.domain.value_objects.executed_step import ExecutedStep
from src.domain.value_objects.transformation_step import TransformAction


def _make_result(**overrides) -> CuratedResult:
    defaults = dict(
        dataset_id="ds-1",
        etl_run_id="run-1",
        plan_id="plan-1",
        strategy="conservative",
        status="completed",
        curated_file_path="/tmp/curated.csv",
        original_row_count=100,
        curated_row_count=95,
        original_column_count=10,
        curated_column_count=8,
        original_null_count=20,
        curated_null_count=0,
        executed_steps=[
            ExecutedStep(
                action=TransformAction.FILL_NULLS_MEDIAN,
                column_name="age",
                success=True,
                rows_before=100,
                rows_after=100,
                columns_before=10,
                columns_after=10,
                detail="Mediana aplicada",
            ),
            ExecutedStep(
                action=TransformAction.DROP_COLUMN,
                column_name="junk",
                success=True,
                rows_before=100,
                rows_after=100,
                columns_before=10,
                columns_after=9,
                detail="Columna eliminada",
            ),
        ],
        execution_time_ms=42,
        execution_mode="manual",
    )
    defaults.update(overrides)
    return CuratedResult(**defaults)


class TestBuildSystemPrompt:

    def test_contains_guardrails(self) -> None:
        prompt = build_system_prompt()
        assert "ÚNICAMENTE" in prompt
        assert "NO inventes" in prompt
        assert "NUNCA decidir" in prompt

    def test_contains_section_headers(self) -> None:
        prompt = build_system_prompt()
        for header in ("## RESUMEN", "## CALIDAD_ORIGINAL", "## TRANSFORMACIONES", "## RESULTADO", "## RECOMENDACIONES"):
            assert header in prompt


class TestBuildUserPrompt:

    def test_contains_etl_context_marker(self) -> None:
        result = _make_result()
        prompt = build_user_prompt(result)
        assert "== ETL CONTEXT ==" in prompt

    def test_contains_metrics(self) -> None:
        result = _make_result()
        prompt = build_user_prompt(result)
        assert "100" in prompt  # original_row_count
        assert "95" in prompt   # curated_row_count
        assert "42ms" in prompt

    def test_contains_step_details(self) -> None:
        result = _make_result()
        prompt = build_user_prompt(result)
        assert "fill_nulls_median" in prompt
        assert "age" in prompt
        assert "drop_column" in prompt

    def test_contains_strategy_and_mode(self) -> None:
        result = _make_result(strategy="aggressive", execution_mode="auto_safe")
        prompt = build_user_prompt(result)
        assert "aggressive" in prompt
        assert "auto_safe" in prompt
