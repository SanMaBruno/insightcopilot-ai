from __future__ import annotations

import time
from uuid import uuid4

from src.application.services.column_classifier import classify_columns
from src.application.services.transformation_planner import generate_plan_steps
from src.application.use_cases.get_dataset_by_id_use_case import GetDatasetByIdUseCase
from src.domain.entities.curated_result import CuratedResult
from src.domain.entities.transformation_plan import PlanStatus, TransformationPlan
from src.domain.repositories.curated_result_repository import CuratedResultRepository
from src.domain.repositories.dataset_loader import DatasetLoader
from src.domain.repositories.dataset_repository import DatasetRepository
from src.domain.repositories.file_storage import FileStorage
from src.domain.repositories.transformation_engine import TransformationEngine


class ExecuteEtlUseCase:

    def __init__(
        self,
        repository: DatasetRepository,
        loader: DatasetLoader,
        engine: TransformationEngine,
        file_storage: FileStorage,
        curated_repo: CuratedResultRepository,
    ) -> None:
        self._repository = repository
        self._loader = loader
        self._engine = engine
        self._file_storage = file_storage
        self._curated_repo = curated_repo

    def execute(
        self,
        dataset_id: str,
        etl_run_id: str,
        quality_assessment_id: str,
        strategy: str = "conservative",
    ) -> CuratedResult:
        dataset = GetDatasetByIdUseCase(self._repository).execute(dataset_id)
        raw = self._loader.load(dataset.file_path)

        # Regenerate plan server-side (deterministic)
        classifications = classify_columns(raw)
        steps = generate_plan_steps(classifications, raw.duplicate_row_count, strategy)

        plan = TransformationPlan(
            dataset_id=dataset.id,
            etl_run_id=etl_run_id,
            quality_assessment_id=quality_assessment_id,
            strategy=strategy,
            steps=steps,
            status=PlanStatus.EXECUTED,
        )

        # Execute transformations
        start = time.monotonic()
        output = self._engine.execute(dataset.file_path, steps)
        elapsed_ms = int((time.monotonic() - start) * 1000)

        # Persist curated CSV
        curated_filename = f"curated_{dataset.name}"
        curated_path = self._file_storage.save(curated_filename, output.csv_bytes)

        original_null_count = sum(raw.null_counts.values())

        result = CuratedResult(
            dataset_id=dataset.id,
            etl_run_id=etl_run_id,
            plan_id=plan.id,
            strategy=strategy,
            status="completed",
            curated_file_path=curated_path,
            original_row_count=raw.row_count,
            curated_row_count=output.row_count,
            original_column_count=len(raw.columns),
            curated_column_count=output.column_count,
            original_null_count=original_null_count,
            curated_null_count=output.null_count,
            executed_steps=output.executed_steps,
            execution_time_ms=elapsed_ms,
        )

        self._curated_repo.save(result)
        return result
