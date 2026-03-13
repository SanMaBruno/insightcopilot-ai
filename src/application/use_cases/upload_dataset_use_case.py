from __future__ import annotations

from src.domain.entities.dataset import Dataset
from src.domain.repositories.dataset_repository import DatasetRepository
from src.domain.repositories.file_storage import FileStorage


class UploadDatasetUseCase:

    def __init__(
        self, repository: DatasetRepository, file_storage: FileStorage
    ) -> None:
        self._repository = repository
        self._file_storage = file_storage

    def execute(self, name: str, filename: str, content: bytes) -> Dataset:
        file_path = self._file_storage.save(filename, content)
        dataset = Dataset(name=name, file_path=file_path, source_type="csv")
        self._repository.save(dataset)
        return dataset
