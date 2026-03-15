from fastapi import APIRouter, Depends, HTTPException

from src.application.use_cases.assess_quality_use_case import AssessQualityUseCase
from src.application.use_cases.generate_transform_plan_use_case import (
    GenerateTransformPlanUseCase,
)
from src.application.use_cases.get_dataset_by_id_use_case import DatasetNotFoundError
from src.domain.repositories.dataset_loader import DatasetLoader
from src.domain.repositories.dataset_repository import DatasetRepository
from src.infrastructure.files.csv_dataset_loader import FileLoadError
from src.presentation.api.dependencies import get_dataset_loader, get_dataset_repository
from src.presentation.api.schemas.etl import (
    ColumnClassificationResponse,
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
