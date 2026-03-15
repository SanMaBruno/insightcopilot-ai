from __future__ import annotations

from typing import Optional

from src.domain.entities.curated_result import CuratedResult
from src.domain.repositories.curated_result_repository import CuratedResultRepository


class CuratedResultNotFoundError(Exception):
    def __init__(self, dataset_id: str, etl_run_id: str) -> None:
        self.message = (
            f"No se encontró resultado curado para dataset '{dataset_id}' "
            f"con etl_run_id '{etl_run_id}'"
        )
        super().__init__(self.message)


class GetCuratedResultUseCase:

    def __init__(self, curated_repo: CuratedResultRepository) -> None:
        self._curated_repo = curated_repo

    def execute(self, dataset_id: str, etl_run_id: str) -> CuratedResult:
        result = self._curated_repo.get_by_run(dataset_id, etl_run_id)
        if result is None:
            raise CuratedResultNotFoundError(dataset_id, etl_run_id)
        return result
