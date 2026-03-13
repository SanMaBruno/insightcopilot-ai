from __future__ import annotations

from src.domain.entities.dataset import Dataset
from src.domain.repositories.dataset_repository import DatasetRepository


class InMemoryDatasetRepository(DatasetRepository):

    def __init__(self) -> None:
        self._storage: dict[str, Dataset] = {}

    def save(self, dataset: Dataset) -> None:
        self._storage[dataset.id] = dataset

    def get_by_id(self, dataset_id: str) -> Dataset | None:
        return self._storage.get(dataset_id)

    def list_all(self) -> list[Dataset]:
        return list(self._storage.values())
