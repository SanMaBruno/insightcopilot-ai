from __future__ import annotations

from src.application.services.column_classifier import classify_columns
from src.application.services.transformation_planner import generate_plan_steps
from src.application.use_cases.get_dataset_by_id_use_case import GetDatasetByIdUseCase
from src.domain.entities.transformation_plan import TransformationPlan
from src.domain.repositories.dataset_loader import DatasetLoader
from src.domain.repositories.dataset_repository import DatasetRepository


class GenerateTransformPlanUseCase:

    def __init__(
        self,
        repository: DatasetRepository,
        loader: DatasetLoader,
    ) -> None:
        self._repository = repository
        self._loader = loader

    def execute(
        self,
        dataset_id: str,
        etl_run_id: str,
        quality_assessment_id: str,
        strategy: str = "conservative",
    ) -> TransformationPlan:
        dataset = GetDatasetByIdUseCase(self._repository).execute(dataset_id)
        raw = self._loader.load(dataset.file_path)

        classifications = classify_columns(raw)
        steps = generate_plan_steps(classifications, raw.duplicate_row_count, strategy)

        return TransformationPlan(
            dataset_id=dataset.id,
            etl_run_id=etl_run_id,
            quality_assessment_id=quality_assessment_id,
            strategy=strategy,
            steps=steps,
        )
