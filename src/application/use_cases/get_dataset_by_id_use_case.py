from src.domain.entities.dataset import Dataset
from src.domain.repositories.dataset_repository import DatasetRepository
from src.shared.exceptions.base import DomainError


class DatasetNotFoundError(DomainError):
    pass


class GetDatasetByIdUseCase:

    def __init__(self, repository: DatasetRepository) -> None:
        self._repository = repository

    def execute(self, dataset_id: str) -> Dataset:
        dataset = self._repository.get_by_id(dataset_id)
        if dataset is None:
            raise DatasetNotFoundError(f"Dataset '{dataset_id}' no encontrado")
        return dataset
