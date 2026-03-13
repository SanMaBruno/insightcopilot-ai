import os

import pytest

from src.application.use_cases.get_dataset_by_id_use_case import DatasetNotFoundError
from src.application.use_cases.profile_dataset_use_case import ProfileDatasetUseCase
from src.domain.entities.dataset import Dataset
from src.infrastructure.files.csv_dataset_loader import CsvDatasetLoader, FileLoadError
from src.infrastructure.persistence.in_memory_dataset_repository import (
    InMemoryDatasetRepository,
)

SAMPLE_CSV = os.path.join(os.path.dirname(__file__), "..", "..", "data", "sample", "test_data.csv")


class TestProfileDatasetUseCase:

    def setup_method(self) -> None:
        self.repo = InMemoryDatasetRepository()
        self.loader = CsvDatasetLoader()
        self.use_case = ProfileDatasetUseCase(repository=self.repo, loader=self.loader)

    def test_profiles_existing_dataset(self) -> None:
        ds = Dataset(name="test", file_path=SAMPLE_CSV, source_type="csv")
        self.repo.save(ds)

        profile = self.use_case.execute(ds.id)

        assert profile.dataset_id == ds.id
        assert profile.row_count == 3
        assert profile.column_count == 3
        assert len(profile.columns) == 3
        assert profile.columns[0].name == "name"
        assert profile.columns[1].null_count == 1

    def test_raises_when_dataset_not_found(self) -> None:
        with pytest.raises(DatasetNotFoundError):
            self.use_case.execute("nonexistent")

    def test_raises_when_file_missing(self) -> None:
        ds = Dataset(name="bad", file_path="/missing.csv", source_type="csv")
        self.repo.save(ds)

        with pytest.raises(FileLoadError):
            self.use_case.execute(ds.id)
