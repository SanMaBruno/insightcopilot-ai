from src.application.services.insight_generator import generate_insights
from src.domain.entities.dataset_profile import DatasetProfile
from src.domain.value_objects.column_profile import ColumnProfile


def _make_profile(
    columns: list[ColumnProfile],
    row_count: int = 100,
    dataset_id: str = "ds-1",
) -> DatasetProfile:
    return DatasetProfile(
        dataset_id=dataset_id,
        row_count=row_count,
        column_count=len(columns),
        columns=columns,
    )


class TestInsightGenerator:

    def test_summary_includes_counts(self) -> None:
        profile = _make_profile([
            ColumnProfile(name="age", dtype="int64", null_count=0, unique_count=50),
            ColumnProfile(name="name", dtype="object", null_count=0, unique_count=80),
        ])

        report = generate_insights(profile)

        assert "100 filas" in report.summary
        assert "2 columnas" in report.summary
        assert "1 numéricas" in report.summary
        assert "1 categóricas" in report.summary

    def test_detects_numeric_and_categorical(self) -> None:
        profile = _make_profile([
            ColumnProfile(name="id", dtype="int64", null_count=0, unique_count=100),
            ColumnProfile(name="score", dtype="float64", null_count=0, unique_count=50),
            ColumnProfile(name="city", dtype="object", null_count=0, unique_count=10),
        ])

        report = generate_insights(profile)
        messages = [i.message for i in report.insights]

        assert any("id" in m and "score" in m and "numéricas" in m for m in messages)
        assert any("city" in m and "categóricas" in m for m in messages)

    def test_detects_high_null_columns(self) -> None:
        profile = _make_profile([
            ColumnProfile(name="notes", dtype="object", null_count=80, unique_count=5),
        ])

        report = generate_insights(profile)
        messages = [i.message for i in report.insights]

        assert any("notes" in m and "nulos" in m.lower() for m in messages)

    def test_detects_constant_columns(self) -> None:
        profile = _make_profile([
            ColumnProfile(name="status", dtype="object", null_count=0, unique_count=1),
        ])

        report = generate_insights(profile)
        messages = [i.message for i in report.insights]

        assert any("status" in m and "un solo valor" in m for m in messages)

    def test_warns_on_empty_dataset(self) -> None:
        profile = _make_profile([], row_count=0)

        report = generate_insights(profile)

        assert any("vacío" in w for w in report.warnings)

    def test_warns_on_completely_empty_columns(self) -> None:
        profile = _make_profile([
            ColumnProfile(name="empty_col", dtype="object", null_count=100, unique_count=0),
        ])

        report = generate_insights(profile)

        assert any("empty_col" in w for w in report.warnings)

    def test_no_warnings_on_healthy_dataset(self) -> None:
        profile = _make_profile([
            ColumnProfile(name="id", dtype="int64", null_count=0, unique_count=100),
        ])

        report = generate_insights(profile)

        assert report.warnings == []
