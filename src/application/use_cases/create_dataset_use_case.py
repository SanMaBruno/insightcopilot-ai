from src.domain.entities.dataset import Dataset
from src.domain.repositories.dataset_repository import DatasetRepository


class CreateDatasetUseCase:

    def __init__(self, repository: DatasetRepository) -> None:
        self._repository = repository

    def execute(self, name: str, file_path: str, source_type: str) -> Dataset:
        dataset = Dataset(name=name, file_path=file_path, source_type=source_type)
        self._repository.save(dataset)
        return dataset
