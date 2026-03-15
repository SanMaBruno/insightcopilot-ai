from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from src.application.use_cases.auto_etl_use_case import AutoEtlUseCase
from src.domain.entities.curated_result import CuratedResult
from src.domain.repositories.curated_result_repository import CuratedResultRepository
from src.domain.repositories.dataset_loader import DatasetLoader, RawDatasetData
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
        ],
        row_count=97,
        column_count=2,
        null_count=1,
    )


@pytest.fixture()
def deps():
    loader = MagicMock(spec=DatasetLoader)
    loader.load.return_value = _make_raw()
    engine = MagicMock(spec=TransformationEngine)
    engine.execute.return_value = _make_output()
    file_storage = MagicMock(spec=FileStorage)
    file_storage.save.return_value = "/data/curated/curated_test.csv"
    curated_repo = MagicMock(spec=CuratedResultRepository)
    return loader, engine, file_storage, curated_repo


class TestAutoEtlUseCase:

    def test_returns_curated_result(self, deps):
        loader, engine, fs, cr = deps
        uc = AutoEtlUseCase(loader=loader, engine=engine, file_storage=fs, curated_repo=cr)

        result = uc.execute("ds-1", "/tmp/test.csv", "test.csv")

        assert result.dataset_id == "ds-1"
        assert result.status == "completed"
        assert result.strategy == "conservative"
        assert result.execution_mode == "auto_safe"
        assert result.curated_file_path == "/data/curated/curated_test.csv"
        assert result.original_row_count == 100
        assert result.curated_row_count == 97

    def test_execution_mode_is_auto_safe(self, deps):
        loader, engine, fs, cr = deps
        uc = AutoEtlUseCase(loader=loader, engine=engine, file_storage=fs, curated_repo=cr)

        result = uc.execute("ds-1", "/tmp/test.csv", "test.csv")

        assert result.execution_mode == "auto_safe"

    def test_strategy_is_always_conservative(self, deps):
        loader, engine, fs, cr = deps
        uc = AutoEtlUseCase(loader=loader, engine=engine, file_storage=fs, curated_repo=cr)

        result = uc.execute("ds-1", "/tmp/test.csv", "test.csv")

        assert result.strategy == "conservative"

    def test_saves_curated_result(self, deps):
        loader, engine, fs, cr = deps
        uc = AutoEtlUseCase(loader=loader, engine=engine, file_storage=fs, curated_repo=cr)

        result = uc.execute("ds-1", "/tmp/test.csv", "test.csv")

        cr.save.assert_called_once_with(result)

    def test_saves_curated_csv(self, deps):
        loader, engine, fs, cr = deps
        uc = AutoEtlUseCase(loader=loader, engine=engine, file_storage=fs, curated_repo=cr)

        uc.execute("ds-1", "/tmp/test.csv", "test.csv")

        fs.save.assert_called_once_with("curated_test.csv", b"a,b\n1,x\n2,y\n")

    def test_loads_dataset_by_file_path(self, deps):
        loader, engine, fs, cr = deps
        uc = AutoEtlUseCase(loader=loader, engine=engine, file_storage=fs, curated_repo=cr)

        uc.execute("ds-1", "/tmp/test.csv", "test.csv")

        loader.load.assert_called_once_with("/tmp/test.csv")

    def test_etl_run_id_is_unique(self, deps):
        loader, engine, fs, cr = deps
        uc = AutoEtlUseCase(loader=loader, engine=engine, file_storage=fs, curated_repo=cr)

        r1 = uc.execute("ds-1", "/tmp/test.csv", "test.csv")
        r2 = uc.execute("ds-1", "/tmp/test.csv", "test.csv")

        assert r1.etl_run_id != r2.etl_run_id

    def test_null_counts_computed(self, deps):
        loader, engine, fs, cr = deps
        uc = AutoEtlUseCase(loader=loader, engine=engine, file_storage=fs, curated_repo=cr)

        result = uc.execute("ds-1", "/tmp/test.csv", "test.csv")

        assert result.original_null_count == 15  # 0 + 5 + 10
        assert result.curated_null_count == 1
