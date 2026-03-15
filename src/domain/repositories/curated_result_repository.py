from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from src.domain.entities.curated_result import CuratedResult


class CuratedResultRepository(ABC):

    @abstractmethod
    def save(self, result: CuratedResult) -> None: ...

    @abstractmethod
    def get_by_run(
        self, dataset_id: str, etl_run_id: str,
    ) -> Optional[CuratedResult]: ...

    @abstractmethod
    def get_latest_by_dataset(
        self, dataset_id: str,
    ) -> Optional[CuratedResult]: ...
