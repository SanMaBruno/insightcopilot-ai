from src.application.services.quality_scorer import compute_quality_score
from src.domain.repositories.dataset_loader import RawDatasetData
from src.domain.value_objects.column_classification import ColumnClassification, ColumnRole


def _make_classification(
    name: str, role: ColumnRole, dtype: str = "object",
) -> ColumnClassification:
    return ColumnClassification(
        column_name=name, dtype=dtype, role=role,
        null_ratio=0.0, unique_ratio=0.5, reason="test",
    )


class TestQualityScorer:

    def test_perfect_dataset(self) -> None:
        raw = RawDatasetData(
            columns=["a", "b"],
            row_count=100,
            dtypes={"a": "int64", "b": "object"},
            null_counts={"a": 0, "b": 0},
            unique_counts={"a": 100, "b": 50},
        )
        classifications = [
            _make_classification("a", ColumnRole.VALUABLE_NUMERIC, "int64"),
            _make_classification("b", ColumnRole.VALUABLE_CATEGORICAL),
        ]

        score = compute_quality_score(raw, classifications, duplicate_row_count=0)

        assert score.completeness == 1.0
        assert score.uniqueness == 1.0
        assert score.validity == 1.0
        assert score.overall > 0.9

    def test_dataset_with_nulls(self) -> None:
        raw = RawDatasetData(
            columns=["a"],
            row_count=100,
            dtypes={"a": "int64"},
            null_counts={"a": 50},
            unique_counts={"a": 50},
        )
        classifications = [
            _make_classification("a", ColumnRole.VALUABLE_NUMERIC, "int64"),
        ]

        score = compute_quality_score(raw, classifications, duplicate_row_count=0)

        assert score.completeness == 0.5

    def test_dataset_with_duplicates(self) -> None:
        raw = RawDatasetData(
            columns=["a"],
            row_count=100,
            dtypes={"a": "int64"},
            null_counts={"a": 0},
            unique_counts={"a": 80},
        )
        classifications = [
            _make_classification("a", ColumnRole.VALUABLE_NUMERIC, "int64"),
        ]

        score = compute_quality_score(raw, classifications, duplicate_row_count=20)

        assert score.uniqueness == 0.8

    def test_invalid_columns_reduce_validity(self) -> None:
        raw = RawDatasetData(
            columns=["a", "b", "c"],
            row_count=100,
            dtypes={"a": "int64", "b": "object", "c": "object"},
            null_counts={"a": 0, "b": 0, "c": 100},
            unique_counts={"a": 100, "b": 1, "c": 0},
        )
        classifications = [
            _make_classification("a", ColumnRole.VALUABLE_NUMERIC, "int64"),
            _make_classification("b", ColumnRole.CONSTANT),
            _make_classification("c", ColumnRole.EMPTY),
        ]

        score = compute_quality_score(raw, classifications, duplicate_row_count=0)

        assert round(score.validity, 4) == round(1 / 3, 4)

    def test_overall_is_weighted_average(self) -> None:
        raw = RawDatasetData(
            columns=["a"],
            row_count=100,
            dtypes={"a": "int64"},
            null_counts={"a": 0},
            unique_counts={"a": 100},
        )
        classifications = [
            _make_classification("a", ColumnRole.VALUABLE_NUMERIC, "int64"),
        ]

        score = compute_quality_score(raw, classifications, duplicate_row_count=0)

        expected = 0.35 * 1.0 + 0.20 * 1.0 + 0.20 * 1.0 + 0.25 * 1.0
        assert score.overall == round(expected, 4)
