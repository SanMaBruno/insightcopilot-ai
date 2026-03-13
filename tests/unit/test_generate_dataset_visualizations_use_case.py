from __future__ import annotations

import pytest

from src.application.use_cases.generate_dataset_visualizations_use_case import (
    GenerateDatasetVisualizationsUseCase,
)
from src.application.use_cases.get_dataset_by_id_use_case import DatasetNotFoundError
from src.domain.entities.chart_result import ChartResult, ChartSeries, InteractiveChartSpec
from src.domain.entities.dataset import Dataset
from src.domain.repositories.chart_generator import ChartGenerator
from src.infrastructure.persistence.in_memory_dataset_repository import (
    InMemoryDatasetRepository,
)


class _FakeChartGenerator(ChartGenerator):

    def generate(self, file_path: str) -> list[ChartResult]:
        return [
            ChartResult(
                chart_type="test_chart",
                title="Test",
                columns=["col_a"],
                image_base64="AAAA",
                interactive_spec=InteractiveChartSpec(
                    chart_kind="column",
                    subtitle="Demo",
                    categories=["A", "B"],
                    series=[ChartSeries(name="Serie", data=[1.0, 2.0])],
                    x_axis_label="X",
                    y_axis_label="Y",
                    tooltip_suffix=" pts",
                    source_label="Fake source",
                ),
            )
        ]


class TestGenerateDatasetVisualizationsUseCase:

    def setup_method(self) -> None:
        self.repo = InMemoryDatasetRepository()
        self.chart_gen = _FakeChartGenerator()
        self.use_case = GenerateDatasetVisualizationsUseCase(
            repository=self.repo, chart_generator=self.chart_gen
        )

    def test_generates_visualizations_for_existing_dataset(self) -> None:
        ds = Dataset(name="test", file_path="/data/test.csv", source_type="csv")
        self.repo.save(ds)

        result = self.use_case.execute(ds.id)

        assert result.dataset_id == ds.id
        assert len(result.charts) == 1
        assert result.charts[0].chart_type == "test_chart"
        assert result.charts[0].interactive_spec is not None

    def test_raises_when_dataset_not_found(self) -> None:
        with pytest.raises(DatasetNotFoundError):
            self.use_case.execute("nonexistent")
