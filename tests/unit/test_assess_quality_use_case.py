from unittest.mock import MagicMock

from src.application.use_cases.assess_quality_use_case import AssessQualityUseCase
from src.domain.entities.dataset import Dataset
from src.domain.repositories.dataset_loader import RawDatasetData
from src.domain.value_objects.column_classification import ColumnRole


def _make_dataset() -> Dataset:
    return Dataset(name="test", file_path="/tmp/test.csv", source_type="csv", id="ds-1")


def _make_raw() -> RawDatasetData:
    return RawDatasetData(
        columns=["id", "age", "city", "empty_col"],
        row_count=100,
        dtypes={"id": "int64", "age": "float64", "city": "object", "empty_col": "object"},
        null_counts={"id": 0, "age": 10, "city": 2, "empty_col": 100},
        unique_counts={"id": 99, "age": 60, "city": 15, "empty_col": 0},
        duplicate_row_count=5,
    )


class TestAssessQualityUseCase:

    def test_returns_assessment_with_all_fields(self) -> None:
        repo = MagicMock()
        repo.get_by_id.return_value = _make_dataset()
        loader = MagicMock()
        loader.load.return_value = _make_raw()

        result = AssessQualityUseCase(repository=repo, loader=loader).execute("ds-1")

        assert result.dataset_id == "ds-1"
        assert result.etl_run_id
        assert result.row_count == 100
        assert result.column_count == 4
        assert result.duplicate_row_count == 5
        assert len(result.column_assessments) == 4
        assert result.score.overall > 0

    def test_classifies_columns_correctly(self) -> None:
        repo = MagicMock()
        repo.get_by_id.return_value = _make_dataset()
        loader = MagicMock()
        loader.load.return_value = _make_raw()

        result = AssessQualityUseCase(repository=repo, loader=loader).execute("ds-1")
        roles = {c.column_name: c.role for c in result.column_assessments}

        assert roles["id"] == ColumnRole.IDENTIFIER
        assert roles["age"] == ColumnRole.VALUABLE_NUMERIC
        assert roles["city"] == ColumnRole.VALUABLE_CATEGORICAL
        assert roles["empty_col"] == ColumnRole.EMPTY

    def test_score_reflects_empty_column(self) -> None:
        repo = MagicMock()
        repo.get_by_id.return_value = _make_dataset()
        loader = MagicMock()
        loader.load.return_value = _make_raw()

        result = AssessQualityUseCase(repository=repo, loader=loader).execute("ds-1")

        assert result.score.validity < 1.0
        assert result.score.completeness < 1.0
