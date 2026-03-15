from src.application.services.column_classifier import classify_columns
from src.domain.repositories.dataset_loader import RawDatasetData
from src.domain.value_objects.column_classification import ColumnRole


def _make_raw(
    columns: list[str],
    dtypes: dict[str, str],
    null_counts: dict[str, int],
    unique_counts: dict[str, int],
    row_count: int = 100,
) -> RawDatasetData:
    return RawDatasetData(
        columns=columns,
        row_count=row_count,
        dtypes=dtypes,
        null_counts=null_counts,
        unique_counts=unique_counts,
    )


class TestColumnClassifier:

    def test_empty_column(self) -> None:
        raw = _make_raw(
            columns=["col_a"],
            dtypes={"col_a": "object"},
            null_counts={"col_a": 100},
            unique_counts={"col_a": 0},
        )

        result = classify_columns(raw)

        assert len(result) == 1
        assert result[0].role == ColumnRole.EMPTY
        assert result[0].null_ratio == 1.0

    def test_constant_column(self) -> None:
        raw = _make_raw(
            columns=["status"],
            dtypes={"status": "object"},
            null_counts={"status": 0},
            unique_counts={"status": 1},
        )

        result = classify_columns(raw)

        assert result[0].role == ColumnRole.CONSTANT

    def test_high_null_column(self) -> None:
        raw = _make_raw(
            columns=["notes"],
            dtypes={"notes": "object"},
            null_counts={"notes": 60},
            unique_counts={"notes": 10},
        )

        result = classify_columns(raw)

        assert result[0].role == ColumnRole.HIGH_NULL
        assert result[0].null_ratio == 0.6

    def test_identifier_by_name_and_cardinality(self) -> None:
        raw = _make_raw(
            columns=["user_id"],
            dtypes={"user_id": "int64"},
            null_counts={"user_id": 0},
            unique_counts={"user_id": 98},
        )

        result = classify_columns(raw)

        assert result[0].role == ColumnRole.IDENTIFIER

    def test_identifier_object_type(self) -> None:
        raw = _make_raw(
            columns=["transaction_id"],
            dtypes={"transaction_id": "object"},
            null_counts={"transaction_id": 0},
            unique_counts={"transaction_id": 95},
        )

        result = classify_columns(raw)

        assert result[0].role == ColumnRole.IDENTIFIER

    def test_noise_high_cardinality_text(self) -> None:
        raw = _make_raw(
            columns=["description"],
            dtypes={"description": "object"},
            null_counts={"description": 0},
            unique_counts={"description": 90},
            row_count=100,
        )

        result = classify_columns(raw)

        assert result[0].role == ColumnRole.NOISE

    def test_date_candidate_by_name(self) -> None:
        raw = _make_raw(
            columns=["fecha_registro"],
            dtypes={"fecha_registro": "object"},
            null_counts={"fecha_registro": 0},
            unique_counts={"fecha_registro": 50},
        )

        result = classify_columns(raw)

        assert result[0].role == ColumnRole.DATE_CANDIDATE
        assert "parseable_as_date" in result[0].secondary_flags

    def test_low_variance(self) -> None:
        raw = _make_raw(
            columns=["flag"],
            dtypes={"flag": "object"},
            null_counts={"flag": 0},
            unique_counts={"flag": 2},
            row_count=100,
        )

        result = classify_columns(raw)

        assert result[0].role == ColumnRole.LOW_VARIANCE

    def test_valuable_numeric(self) -> None:
        raw = _make_raw(
            columns=["salary"],
            dtypes={"salary": "float64"},
            null_counts={"salary": 5},
            unique_counts={"salary": 80},
        )

        result = classify_columns(raw)

        assert result[0].role == ColumnRole.VALUABLE_NUMERIC

    def test_valuable_categorical(self) -> None:
        raw = _make_raw(
            columns=["city"],
            dtypes={"city": "object"},
            null_counts={"city": 2},
            unique_counts={"city": 25},
        )

        result = classify_columns(raw)

        assert result[0].role == ColumnRole.VALUABLE_CATEGORICAL

    def test_priority_empty_over_identifier(self) -> None:
        """EMPTY should win even if name matches ID pattern."""
        raw = _make_raw(
            columns=["user_id"],
            dtypes={"user_id": "int64"},
            null_counts={"user_id": 100},
            unique_counts={"user_id": 0},
        )

        result = classify_columns(raw)

        assert result[0].role == ColumnRole.EMPTY

    def test_multiple_columns_classified(self) -> None:
        raw = _make_raw(
            columns=["id", "age", "city", "empty_col"],
            dtypes={"id": "int64", "age": "float64", "city": "object", "empty_col": "object"},
            null_counts={"id": 0, "age": 3, "city": 0, "empty_col": 100},
            unique_counts={"id": 99, "age": 60, "city": 15, "empty_col": 0},
        )

        result = classify_columns(raw)
        roles = {c.column_name: c.role for c in result}

        assert roles["id"] == ColumnRole.IDENTIFIER
        assert roles["age"] == ColumnRole.VALUABLE_NUMERIC
        assert roles["city"] == ColumnRole.VALUABLE_CATEGORICAL
        assert roles["empty_col"] == ColumnRole.EMPTY

    def test_secondary_flags_on_numeric_low_cardinality(self) -> None:
        raw = _make_raw(
            columns=["rating"],
            dtypes={"rating": "int64"},
            null_counts={"rating": 0},
            unique_counts={"rating": 3},
            row_count=500,
        )

        result = classify_columns(raw)

        assert result[0].role == ColumnRole.VALUABLE_NUMERIC
        assert "low_cardinality_numeric" in result[0].secondary_flags

    def test_empty_dataset(self) -> None:
        raw = _make_raw(
            columns=["a"],
            dtypes={"a": "object"},
            null_counts={"a": 0},
            unique_counts={"a": 0},
            row_count=0,
        )

        result = classify_columns(raw)

        assert len(result) == 1
