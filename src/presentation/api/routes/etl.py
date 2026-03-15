import os

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse

from src.application.use_cases.assess_quality_use_case import AssessQualityUseCase
from src.application.use_cases.execute_etl_use_case import ExecuteEtlUseCase
from src.application.use_cases.generate_transform_plan_use_case import (
    GenerateTransformPlanUseCase,
)
from src.application.use_cases.get_curated_result_use_case import (
    CuratedResultNotFoundError,
    GetCuratedResultUseCase,
)
from src.application.use_cases.generate_etl_narrative_use_case import (
    CuratedResultNotFoundError as NarrativeNotFoundError,
    GenerateEtlNarrativeUseCase,
)
from src.application.use_cases.get_dataset_by_id_use_case import DatasetNotFoundError
from src.domain.llm_client import LlmClient
from src.domain.repositories.curated_result_repository import CuratedResultRepository
from src.domain.repositories.dataset_loader import DatasetLoader
from src.domain.repositories.dataset_repository import DatasetRepository
from src.domain.repositories.file_storage import FileStorage
from src.domain.repositories.transformation_engine import TransformationEngine
from src.infrastructure.files.csv_dataset_loader import FileLoadError
from src.presentation.api.dependencies import (
    get_curated_file_storage,
    get_curated_result_repository,
    get_dataset_loader,
    get_dataset_repository,
    get_llm_client,
    get_transformation_engine,
)
from src.presentation.api.schemas.etl import (
    ColumnClassificationResponse,
    CuratedResultResponse,
    EtlNarrativeRequest,
    EtlNarrativeResponse,
    EtlNarrativeSectionsResponse,
    ExecuteEtlRequest,
    ExecutedStepResponse,
    QualityAssessmentResponse,
    QualityScoreResponse,
    TransformationPlanResponse,
    TransformationStepResponse,
    TransformPlanRequest,
)

router = APIRouter(prefix="/datasets", tags=["etl"])


@router.get(
    "/{dataset_id}/quality", response_model=QualityAssessmentResponse,
)
def assess_quality(
    dataset_id: str,
    repo: DatasetRepository = Depends(get_dataset_repository),  # noqa: B008
    loader: DatasetLoader = Depends(get_dataset_loader),  # noqa: B008
) -> QualityAssessmentResponse:
    try:
        assessment = AssessQualityUseCase(repository=repo, loader=loader).execute(
            dataset_id,
        )
    except DatasetNotFoundError as exc:
        raise HTTPException(status_code=404, detail=exc.message) from exc
    except FileLoadError as exc:
        raise HTTPException(status_code=422, detail=exc.message) from exc

    return QualityAssessmentResponse(
        id=assessment.id,
        dataset_id=assessment.dataset_id,
        etl_run_id=assessment.etl_run_id,
        score=QualityScoreResponse(
            completeness=assessment.score.completeness,
            consistency=assessment.score.consistency,
            uniqueness=assessment.score.uniqueness,
            validity=assessment.score.validity,
            overall=assessment.score.overall,
        ),
        column_assessments=[
            ColumnClassificationResponse(
                column_name=c.column_name,
                dtype=c.dtype,
                role=c.role.value,
                null_ratio=c.null_ratio,
                unique_ratio=c.unique_ratio,
                reason=c.reason,
                secondary_flags=list(c.secondary_flags),
            )
            for c in assessment.column_assessments
        ],
        row_count=assessment.row_count,
        column_count=assessment.column_count,
        duplicate_row_count=assessment.duplicate_row_count,
    )


@router.post(
    "/{dataset_id}/etl/plan", response_model=TransformationPlanResponse,
)
def generate_transform_plan(
    dataset_id: str,
    body: TransformPlanRequest,
    repo: DatasetRepository = Depends(get_dataset_repository),  # noqa: B008
    loader: DatasetLoader = Depends(get_dataset_loader),  # noqa: B008
) -> TransformationPlanResponse:
    try:
        plan = GenerateTransformPlanUseCase(repository=repo, loader=loader).execute(
            dataset_id=dataset_id,
            etl_run_id=body.etl_run_id,
            quality_assessment_id=body.quality_assessment_id,
            strategy=body.strategy,
        )
    except DatasetNotFoundError as exc:
        raise HTTPException(status_code=404, detail=exc.message) from exc
    except FileLoadError as exc:
        raise HTTPException(status_code=422, detail=exc.message) from exc

    return TransformationPlanResponse(
        id=plan.id,
        dataset_id=plan.dataset_id,
        etl_run_id=plan.etl_run_id,
        quality_assessment_id=plan.quality_assessment_id,
        strategy=plan.strategy,
        status=plan.status.value,
        steps=[
            TransformationStepResponse(
                column_name=s.column_name,
                action=s.action.value,
                params=dict(s.params),
                reason=s.reason,
                priority=s.priority,
            )
            for s in plan.steps
        ],
    )


# ---- Phase 2: Execution endpoints ----


def _build_curated_response(result) -> CuratedResultResponse:
    return CuratedResultResponse(
        id=result.id,
        dataset_id=result.dataset_id,
        etl_run_id=result.etl_run_id,
        plan_id=result.plan_id,
        strategy=result.strategy,
        status=result.status,
        curated_file_path=result.curated_file_path,
        original_row_count=result.original_row_count,
        curated_row_count=result.curated_row_count,
        original_column_count=result.original_column_count,
        curated_column_count=result.curated_column_count,
        original_null_count=result.original_null_count,
        curated_null_count=result.curated_null_count,
        executed_steps=[
            ExecutedStepResponse(
                action=s.action.value,
                column_name=s.column_name,
                success=s.success,
                rows_before=s.rows_before,
                rows_after=s.rows_after,
                columns_before=s.columns_before,
                columns_after=s.columns_after,
                detail=s.detail,
            )
            for s in result.executed_steps
        ],
        execution_time_ms=result.execution_time_ms,
        execution_mode=result.execution_mode,
    )


@router.post(
    "/{dataset_id}/etl/execute", response_model=CuratedResultResponse,
)
def execute_etl(
    dataset_id: str,
    body: ExecuteEtlRequest,
    repo: DatasetRepository = Depends(get_dataset_repository),  # noqa: B008
    loader: DatasetLoader = Depends(get_dataset_loader),  # noqa: B008
    engine: TransformationEngine = Depends(get_transformation_engine),  # noqa: B008
    file_storage: FileStorage = Depends(get_curated_file_storage),  # noqa: B008
    curated_repo: CuratedResultRepository = Depends(get_curated_result_repository),  # noqa: B008
) -> CuratedResultResponse:
    try:
        result = ExecuteEtlUseCase(
            repository=repo,
            loader=loader,
            engine=engine,
            file_storage=file_storage,
            curated_repo=curated_repo,
        ).execute(
            dataset_id=dataset_id,
            etl_run_id=body.etl_run_id,
            quality_assessment_id=body.quality_assessment_id,
            strategy=body.strategy,
        )
    except DatasetNotFoundError as exc:
        raise HTTPException(status_code=404, detail=exc.message) from exc
    except FileLoadError as exc:
        raise HTTPException(status_code=422, detail=exc.message) from exc

    return _build_curated_response(result)


@router.get(
    "/{dataset_id}/etl/result", response_model=CuratedResultResponse,
)
def get_curated_result(
    dataset_id: str,
    etl_run_id: str = Query(...),  # noqa: B008
    curated_repo: CuratedResultRepository = Depends(get_curated_result_repository),  # noqa: B008
) -> CuratedResultResponse:
    try:
        result = GetCuratedResultUseCase(curated_repo).execute(dataset_id, etl_run_id)
    except CuratedResultNotFoundError as exc:
        raise HTTPException(status_code=404, detail=exc.message) from exc

    return _build_curated_response(result)


@router.get("/{dataset_id}/etl/download")
def download_curated_csv(
    dataset_id: str,
    etl_run_id: str = Query(...),  # noqa: B008
    curated_repo: CuratedResultRepository = Depends(get_curated_result_repository),  # noqa: B008
) -> FileResponse:
    try:
        result = GetCuratedResultUseCase(curated_repo).execute(dataset_id, etl_run_id)
    except CuratedResultNotFoundError as exc:
        raise HTTPException(status_code=404, detail=exc.message) from exc

    if not os.path.isfile(result.curated_file_path):
        raise HTTPException(status_code=404, detail="Archivo curado no encontrado en disco")

    friendly_name = os.path.basename(result.curated_file_path)

    return FileResponse(
        path=result.curated_file_path,
        media_type="text/csv",
        filename=friendly_name,
        headers={"Content-Disposition": f'attachment; filename="{friendly_name}"'},
    )


# ---- Phase 3: Latest curated result ----


@router.get(
    "/{dataset_id}/etl/latest", response_model=CuratedResultResponse,
)
def get_latest_curated_result(
    dataset_id: str,
    curated_repo: CuratedResultRepository = Depends(get_curated_result_repository),  # noqa: B008
) -> CuratedResultResponse:
    result = curated_repo.get_latest_by_dataset(dataset_id)
    if result is None:
        raise HTTPException(status_code=404, detail="No existe resultado curado para este dataset")
    return _build_curated_response(result)


# ---- Phase 4: ETL Narrative ----


@router.post(
    "/{dataset_id}/etl/narrative", response_model=EtlNarrativeResponse,
)
def generate_etl_narrative(
    dataset_id: str,
    body: EtlNarrativeRequest,
    curated_repo: CuratedResultRepository = Depends(get_curated_result_repository),  # noqa: B008
    llm_client: LlmClient = Depends(get_llm_client),  # noqa: B008
) -> EtlNarrativeResponse:
    try:
        narrative = GenerateEtlNarrativeUseCase(
            curated_repo=curated_repo,
            llm_client=llm_client,
        ).execute(
            dataset_id=dataset_id,
            etl_run_id=body.etl_run_id,
        )
    except NarrativeNotFoundError as exc:
        raise HTTPException(status_code=404, detail=exc.message) from exc

    return EtlNarrativeResponse(
        id=narrative.id,
        dataset_id=narrative.dataset_id,
        etl_run_id=narrative.etl_run_id,
        sections=EtlNarrativeSectionsResponse(
            resumen=narrative.sections.resumen,
            calidad_original=narrative.sections.calidad_original,
            transformaciones=narrative.sections.transformaciones,
            resultado=narrative.sections.resultado,
            recomendaciones=narrative.sections.recomendaciones,
        ),
        execution_mode=narrative.execution_mode,
    )
