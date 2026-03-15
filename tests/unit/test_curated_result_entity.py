from __future__ import annotations

from src.domain.entities.curated_result import CuratedResult
from src.domain.value_objects.executed_step import ExecutedStep
from src.domain.value_objects.transformation_step import TransformAction


def _make_result(**kwargs) -> CuratedResult:
    defaults = dict(
        dataset_id="ds-1",
        etl_run_id="run-1",
        plan_id="plan-1",
        strategy="conservative",
        status="completed",
        curated_file_path="/data/curated/test.csv",
        original_row_count=100,
        curated_row_count=95,
        original_column_count=5,
        curated_column_count=4,
        original_null_count=20,
        curated_null_count=2,
        executed_steps=[
            ExecutedStep(
                action=TransformAction.DROP_COLUMN,
                column_name="empty",
                success=True,
                rows_before=100,
                rows_after=100,
                columns_before=5,
                columns_after=4,
                detail="Columna eliminada",
            ),
        ],
        execution_time_ms=42,
    )
    defaults.update(kwargs)
    return CuratedResult(**defaults)


def test_execution_mode_defaults_to_manual():
    result = _make_result()
    assert result.execution_mode == "manual"


def test_execution_mode_can_be_set():
    result = _make_result(execution_mode="auto_safe")
    assert result.execution_mode == "auto_safe"
