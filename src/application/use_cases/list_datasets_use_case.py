from src.domain.entities.dataset import Dataset
from src.domain.repositories.dataset_repository import DatasetRepository


class ListDatasetsUseCase:

    def __init__(self, repository: DatasetRepository) -> None:
        self._repository = repository

    def execute(self) -> list[Dataset]:
        return self._repository.list_all()
