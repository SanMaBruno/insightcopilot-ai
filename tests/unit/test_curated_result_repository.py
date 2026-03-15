from __future__ import annotations

import pytest

from src.domain.entities.curated_result import CuratedResult
from src.domain.value_objects.executed_step import ExecutedStep
from src.domain.value_objects.transformation_step import TransformAction
from src.infrastructure.persistence.in_memory_curated_result_repository import (
    InMemoryCuratedResultRepository,
)


def _make_result(dataset_id: str = "ds-1", etl_run_id: str = "run-1") -> CuratedResult:
    return CuratedResult(
        dataset_id=dataset_id,
        etl_run_id=etl_run_id,
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


def test_save_and_get():
    repo = InMemoryCuratedResultRepository()
    result = _make_result()
    repo.save(result)

    found = repo.get_by_run("ds-1", "run-1")
    assert found is not None
    assert found.id == result.id
    assert found.curated_row_count == 95


def test_get_not_found():
    repo = InMemoryCuratedResultRepository()

    found = repo.get_by_run("ds-1", "run-999")
    assert found is None


def test_save_overwrites():
    repo = InMemoryCuratedResultRepository()
    r1 = _make_result()
    repo.save(r1)

    r2 = _make_result()
    repo.save(r2)

    found = repo.get_by_run("ds-1", "run-1")
    assert found is not None
    assert found.id == r2.id


def test_different_runs_stored_separately():
    repo = InMemoryCuratedResultRepository()
    r1 = _make_result(etl_run_id="run-1")
    r2 = _make_result(etl_run_id="run-2")
    repo.save(r1)
    repo.save(r2)

    assert repo.get_by_run("ds-1", "run-1") is not None
    assert repo.get_by_run("ds-1", "run-2") is not None
    assert repo.get_by_run("ds-1", "run-1").id != repo.get_by_run("ds-1", "run-2").id


def test_get_latest_by_dataset_returns_most_recent():
    repo = InMemoryCuratedResultRepository()
    r1 = _make_result(etl_run_id="run-1")
    repo.save(r1)
    r2 = _make_result(etl_run_id="run-2")
    repo.save(r2)

    latest = repo.get_latest_by_dataset("ds-1")
    assert latest is not None
    assert latest.etl_run_id == "run-2"


def test_get_latest_by_dataset_none_when_empty():
    repo = InMemoryCuratedResultRepository()
    assert repo.get_latest_by_dataset("ds-1") is None


def test_get_latest_by_dataset_filters_by_dataset_id():
    repo = InMemoryCuratedResultRepository()
    r1 = _make_result(dataset_id="ds-1", etl_run_id="run-1")
    r2 = _make_result(dataset_id="ds-2", etl_run_id="run-2")
    repo.save(r1)
    repo.save(r2)

    latest = repo.get_latest_by_dataset("ds-1")
    assert latest is not None
    assert latest.dataset_id == "ds-1"
