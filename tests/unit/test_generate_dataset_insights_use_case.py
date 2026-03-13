import os

import pytest

from src.application.use_cases.generate_dataset_insights_use_case import (
    GenerateDatasetInsightsUseCase,
)
from src.application.use_cases.get_dataset_by_id_use_case import DatasetNotFoundError
from src.domain.entities.dataset import Dataset
from src.infrastructure.files.csv_dataset_loader import CsvDatasetLoader
from src.infrastructure.persistence.in_memory_dataset_repository import (
    InMemoryDatasetRepository,
)

SAMPLE_CSV = os.path.join(os.path.dirname(__file__), "..", "..", "data", "sample", "test_data.csv")


class TestGenerateDatasetInsightsUseCase:

    def setup_method(self) -> None:
        self.repo = InMemoryDatasetRepository()
        self.loader = CsvDatasetLoader()
        self.use_case = GenerateDatasetInsightsUseCase(
            repository=self.repo, loader=self.loader
        )

    def test_generates_insights_for_existing_dataset(self) -> None:
        ds = Dataset(name="test", file_path=SAMPLE_CSV, source_type="csv")
        self.repo.save(ds)

        report = self.use_case.execute(ds.id)

        assert report.dataset_id == ds.id
        assert "3 filas" in report.summary
        assert len(report.insights) > 0

    def test_raises_when_dataset_not_found(self) -> None:
        with pytest.raises(DatasetNotFoundError):
            self.use_case.execute("nonexistent")
