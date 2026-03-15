from __future__ import annotations

from typing import Optional

from src.domain.entities.curated_result import CuratedResult
from src.domain.repositories.curated_result_repository import CuratedResultRepository


class InMemoryCuratedResultRepository(CuratedResultRepository):

    def __init__(self) -> None:
        self._store: dict[tuple[str, str], CuratedResult] = {}

    def save(self, result: CuratedResult) -> None:
        key = (result.dataset_id, result.etl_run_id)
        self._store[key] = result

    def get_by_run(
        self, dataset_id: str, etl_run_id: str,
    ) -> Optional[CuratedResult]:
        return self._store.get((dataset_id, etl_run_id))
