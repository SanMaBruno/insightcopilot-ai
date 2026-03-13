from __future__ import annotations

from abc import ABC, abstractmethod

from src.domain.entities.dataset import Dataset


class DatasetRepository(ABC):

    @abstractmethod
    def save(self, dataset: Dataset) -> None: ...

    @abstractmethod
    def get_by_id(self, dataset_id: str) -> Dataset | None: ...

    @abstractmethod
    def list_all(self) -> list[Dataset]: ...
