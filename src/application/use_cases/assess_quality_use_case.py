from __future__ import annotations

from uuid import uuid4

from src.application.services.column_classifier import classify_columns
from src.application.services.quality_scorer import compute_quality_score
from src.application.use_cases.get_dataset_by_id_use_case import GetDatasetByIdUseCase
from src.domain.entities.quality_assessment import QualityAssessment
from src.domain.repositories.dataset_loader import DatasetLoader
from src.domain.repositories.dataset_repository import DatasetRepository


class AssessQualityUseCase:

    def __init__(
        self,
        repository: DatasetRepository,
        loader: DatasetLoader,
    ) -> None:
        self._repository = repository
        self._loader = loader

    def execute(self, dataset_id: str) -> QualityAssessment:
        dataset = GetDatasetByIdUseCase(self._repository).execute(dataset_id)
        raw = self._loader.load(dataset.file_path)

        etl_run_id = str(uuid4())
        classifications = classify_columns(raw)
        score = compute_quality_score(raw, classifications, raw.duplicate_row_count)

        return QualityAssessment(
            dataset_id=dataset.id,
            etl_run_id=etl_run_id,
            score=score,
            column_assessments=classifications,
            row_count=raw.row_count,
            column_count=len(raw.columns),
            duplicate_row_count=raw.duplicate_row_count,
        )
