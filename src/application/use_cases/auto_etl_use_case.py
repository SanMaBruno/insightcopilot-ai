from __future__ import annotations

import logging
import time
from uuid import uuid4

from src.application.services.column_classifier import classify_columns
from src.application.services.quality_scorer import compute_quality_score
from src.application.services.transformation_planner import generate_plan_steps
from src.domain.entities.curated_result import CuratedResult
from src.domain.entities.quality_assessment import QualityAssessment
from src.domain.entities.transformation_plan import PlanStatus, TransformationPlan
from src.domain.repositories.curated_result_repository import CuratedResultRepository
from src.domain.repositories.dataset_loader import DatasetLoader
from src.domain.repositories.file_storage import FileStorage
from src.domain.repositories.transformation_engine import TransformationEngine

logger = logging.getLogger(__name__)

_STRATEGY = "conservative"
_EXECUTION_MODE = "auto_safe"


class AutoEtlUseCase:
    """Ejecuta el pipeline ETL completo de forma automática y segura."""

    def __init__(
        self,
        loader: DatasetLoader,
        engine: TransformationEngine,
        file_storage: FileStorage,
        curated_repo: CuratedResultRepository,
    ) -> None:
        self._loader = loader
        self._engine = engine
        self._file_storage = file_storage
        self._curated_repo = curated_repo

    def execute(self, dataset_id: str, file_path: str, dataset_name: str) -> CuratedResult:
        etl_run_id = str(uuid4())

        raw = self._loader.load(file_path)

        classifications = classify_columns(raw)
        score = compute_quality_score(raw, classifications, raw.duplicate_row_count)
        steps = generate_plan_steps(classifications, raw.duplicate_row_count, _STRATEGY)

        plan = TransformationPlan(
            dataset_id=dataset_id,
            etl_run_id=etl_run_id,
            quality_assessment_id=str(uuid4()),
            strategy=_STRATEGY,
            steps=steps,
            status=PlanStatus.EXECUTED,
        )

        start = time.monotonic()
        output = self._engine.execute(file_path, steps)
        elapsed_ms = int((time.monotonic() - start) * 1000)

        curated_filename = f"curated_{dataset_name}"
        curated_path = self._file_storage.save(curated_filename, output.csv_bytes)

        original_null_count = sum(raw.null_counts.values())

        result = CuratedResult(
            dataset_id=dataset_id,
            etl_run_id=etl_run_id,
            plan_id=plan.id,
            strategy=_STRATEGY,
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
            execution_mode=_EXECUTION_MODE,
        )

        self._curated_repo.save(result)

        logger.info(
            "Auto ETL completado | dataset_id=%s | etl_run_id=%s | filas=%d→%d | cols=%d→%d | nulos=%d→%d | %dms",
            dataset_id,
            etl_run_id,
            raw.row_count,
            output.row_count,
            len(raw.columns),
            output.column_count,
            original_null_count,
            output.null_count,
            elapsed_ms,
        )

        return result
