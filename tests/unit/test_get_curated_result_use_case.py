from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from src.application.use_cases.get_curated_result_use_case import (
    CuratedResultNotFoundError,
    GetCuratedResultUseCase,
)
from src.domain.entities.curated_result import CuratedResult
from src.domain.repositories.curated_result_repository import CuratedResultRepository
from src.domain.value_objects.transformation_step import TransformAction
from src.domain.value_objects.executed_step import ExecutedStep


def _make_result() -> CuratedResult:
    return CuratedResult(
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


def test_returns_existing_result():
    repo = MagicMock(spec=CuratedResultRepository)
    repo.get_by_run.return_value = _make_result()
    uc = GetCuratedResultUseCase(repo)

    result = uc.execute("ds-1", "run-1")
    assert result.dataset_id == "ds-1"
    assert result.curated_row_count == 95


def test_raises_when_not_found():
    repo = MagicMock(spec=CuratedResultRepository)
    repo.get_by_run.return_value = None
    uc = GetCuratedResultUseCase(repo)

    with pytest.raises(CuratedResultNotFoundError):
        uc.execute("ds-1", "run-999")
