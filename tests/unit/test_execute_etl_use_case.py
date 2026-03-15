from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from src.application.use_cases.execute_etl_use_case import ExecuteEtlUseCase
from src.domain.entities.dataset import Dataset
from src.domain.repositories.curated_result_repository import CuratedResultRepository
from src.domain.repositories.dataset_loader import DatasetLoader, RawDatasetData
from src.domain.repositories.dataset_repository import DatasetRepository
from src.domain.repositories.file_storage import FileStorage
from src.domain.repositories.transformation_engine import (
    TransformationEngine,
    TransformationOutput,
)
from src.domain.value_objects.executed_step import ExecutedStep
from src.domain.value_objects.transformation_step import TransformAction


def _make_raw() -> RawDatasetData:
    return RawDatasetData(
        columns=["a", "b", "c"],
        row_count=100,
        dtypes={"a": "int64", "b": "object", "c": "float64"},
        null_counts={"a": 0, "b": 5, "c": 10},
        unique_counts={"a": 100, "b": 50, "c": 80},
        duplicate_row_count=3,
    )


def _make_output() -> TransformationOutput:
    return TransformationOutput(
        csv_bytes=b"a,b\n1,x\n2,y\n",
        executed_steps=[
            ExecutedStep(
                action=TransformAction.NORMALIZE_NAMES,
                column_name=None,
                success=True,
                rows_before=100,
                rows_after=100,
                columns_before=3,
                columns_after=3,
                detail="3 nombre(s) normalizado(s)",
            ),
            ExecutedStep(
                action=TransformAction.DROP_COLUMN,
                column_name="c",
                success=True,
                rows_before=100,
                rows_after=100,
                columns_before=3,
                columns_after=2,
                detail="Columna 'c' eliminada",
            ),
        ],
        row_count=97,
        column_count=2,
        null_count=1,
    )


@pytest.fixture()
def deps():
    repo = MagicMock(spec=DatasetRepository)
    repo.get_by_id.return_value = Dataset(
        name="test.csv", file_path="/tmp/test.csv", source_type="csv", id="ds-1",
    )
    loader = MagicMock(spec=DatasetLoader)
    loader.load.return_value = _make_raw()
    engine = MagicMock(spec=TransformationEngine)
    engine.execute.return_value = _make_output()
    file_storage = MagicMock(spec=FileStorage)
    file_storage.save.return_value = "/data/curated/abc_curated_test.csv"
    curated_repo = MagicMock(spec=CuratedResultRepository)

    return repo, loader, engine, file_storage, curated_repo


def test_execute_returns_curated_result(deps):
    repo, loader, engine, fs, cr = deps
    uc = ExecuteEtlUseCase(repo, loader, engine, fs, cr)

    result = uc.execute("ds-1", "run-1", "qa-1", "conservative")

    assert result.dataset_id == "ds-1"
    assert result.etl_run_id == "run-1"
    assert result.status == "completed"
    assert result.strategy == "conservative"
    assert result.curated_file_path == "/data/curated/abc_curated_test.csv"
    assert result.original_row_count == 100
    assert result.curated_row_count == 97
    assert result.original_column_count == 3
    assert result.curated_column_count == 2
    assert result.original_null_count == 15
    assert result.curated_null_count == 1
    assert len(result.executed_steps) == 2


def test_execute_saves_curated_file(deps):
    repo, loader, engine, fs, cr = deps
    uc = ExecuteEtlUseCase(repo, loader, engine, fs, cr)

    uc.execute("ds-1", "run-1", "qa-1")

    fs.save.assert_called_once()
    call_args = fs.save.call_args
    assert "curated_test.csv" in call_args[0][0]


def test_execute_persists_result(deps):
    repo, loader, engine, fs, cr = deps
    uc = ExecuteEtlUseCase(repo, loader, engine, fs, cr)

    result = uc.execute("ds-1", "run-1", "qa-1")

    cr.save.assert_called_once_with(result)


def test_execute_regenerates_plan_internally(deps):
    repo, loader, engine, fs, cr = deps
    uc = ExecuteEtlUseCase(repo, loader, engine, fs, cr)

    uc.execute("ds-1", "run-1", "qa-1", "aggressive")

    engine.execute.assert_called_once()
    steps = engine.execute.call_args[0][1]
    assert len(steps) > 0
    # First step should always be NORMALIZE_NAMES
    assert steps[0].action == TransformAction.NORMALIZE_NAMES


def test_execute_with_aggressive_strategy(deps):
    repo, loader, engine, fs, cr = deps
    uc = ExecuteEtlUseCase(repo, loader, engine, fs, cr)

    result = uc.execute("ds-1", "run-1", "qa-1", "aggressive")

    assert result.strategy == "aggressive"
