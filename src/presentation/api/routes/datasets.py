from fastapi import APIRouter, Depends, HTTPException, UploadFile

from src.application.use_cases.answer_analytical_query_use_case import (
    AnswerAnalyticalQueryUseCase,
)
from src.application.use_cases.create_dataset_use_case import CreateDatasetUseCase
from src.application.use_cases.generate_dataset_insights_use_case import (
    GenerateDatasetInsightsUseCase,
)
from src.application.use_cases.generate_dataset_visualizations_use_case import (
    GenerateDatasetVisualizationsUseCase,
)
from src.application.use_cases.generate_enriched_summary_use_case import (
    GenerateEnrichedSummaryUseCase,
)
from src.application.use_cases.generate_executive_summary_use_case import (
    GenerateExecutiveSummaryUseCase,
)
from src.application.use_cases.get_dataset_by_id_use_case import (
    DatasetNotFoundError,
    GetDatasetByIdUseCase,
)
from src.application.use_cases.list_datasets_use_case import ListDatasetsUseCase
from src.application.use_cases.profile_dataset_use_case import ProfileDatasetUseCase
from src.application.use_cases.rag_query_use_case import RagQueryUseCase
from src.application.use_cases.upload_dataset_use_case import UploadDatasetUseCase
from src.domain.llm_client import LlmClient
from src.domain.repositories.chart_generator import ChartGenerator
from src.domain.repositories.dataset_loader import DatasetLoader
from src.domain.repositories.dataset_repository import DatasetRepository
from src.domain.repositories.document_retriever import DocumentRetriever
from src.domain.repositories.file_storage import FileStorage
from src.infrastructure.files.csv_dataset_loader import FileLoadError
from src.infrastructure.files.matplotlib_chart_generator import ChartGenerationError
from src.infrastructure.llm.openai_llm_client import LlmConfigurationError, LlmGenerationError
from src.infrastructure.rag.openai_embedding_function import (
    EmbeddingConfigurationError,
    EmbeddingGenerationError,
)
from src.presentation.api.dependencies import (
    get_chart_generator,
    get_dataset_loader,
    get_dataset_repository,
    get_document_retriever,
    get_file_storage,
    get_llm_client,
)
from src.presentation.api.schemas.analytical_query import (
    AnalyticalAnswerResponse,
    AnalyticalQueryRequest,
)
from src.presentation.api.schemas.dataset import CreateDatasetRequest, DatasetResponse
from src.presentation.api.schemas.dataset_insight import (
    DatasetInsightReportResponse,
    InsightResponse,
)
from src.presentation.api.schemas.dataset_profile import (
    ColumnProfileResponse,
    DatasetProfileResponse,
)
from src.presentation.api.schemas.dataset_visualization import (
    ChartResultResponse,
    DatasetVisualizationResponse,
)
from src.presentation.api.schemas.executive_summary import (
    ExecutiveSummaryRequest,
    ExecutiveSummaryResponse,
)
from src.presentation.api.schemas.rag_query import (
    DocumentChunkResponse,
    RagQueryRequest,
    RagQueryResponse,
)

router = APIRouter(prefix="/datasets", tags=["datasets"])


def _to_response(dataset) -> DatasetResponse:
    return DatasetResponse(
        id=dataset.id,
        name=dataset.name,
        file_path=dataset.file_path,
        source_type=dataset.source_type,
        created_at=dataset.created_at,
    )


@router.post("", response_model=DatasetResponse, status_code=201)
def create_dataset(
    body: CreateDatasetRequest,
    repo: DatasetRepository = Depends(get_dataset_repository),  # noqa: B008
) -> DatasetResponse:
    dataset = CreateDatasetUseCase(repository=repo).execute(
        name=body.name,
        file_path=body.file_path,
        source_type=body.source_type,
    )
    return _to_response(dataset)

_ALLOWED_CONTENT_TYPES = {"text/csv", "application/csv", "application/vnd.ms-excel"}


@router.post("/upload", response_model=DatasetResponse, status_code=201)
async def upload_dataset(
    file: UploadFile,
    repo: DatasetRepository = Depends(get_dataset_repository),  # noqa: B008
    storage: FileStorage = Depends(get_file_storage),  # noqa: B008
) -> DatasetResponse:
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Solo se permiten archivos CSV.")
    content = await file.read()
    if len(content) == 0:
        raise HTTPException(status_code=400, detail="El archivo está vacío.")
    name = file.filename.rsplit(".", 1)[0]
    dataset = UploadDatasetUseCase(repository=repo, file_storage=storage).execute(
        name=name, filename=file.filename, content=content,
    )
    return _to_response(dataset)

@router.get("", response_model=list[DatasetResponse])
def list_datasets(
    repo: DatasetRepository = Depends(get_dataset_repository),  # noqa: B008
) -> list[DatasetResponse]:
    return [_to_response(ds) for ds in ListDatasetsUseCase(repository=repo).execute()]


@router.get("/{dataset_id}", response_model=DatasetResponse)
def get_dataset(
    dataset_id: str,
    repo: DatasetRepository = Depends(get_dataset_repository),  # noqa: B008
) -> DatasetResponse:
    try:
        dataset = GetDatasetByIdUseCase(repository=repo).execute(dataset_id)
    except DatasetNotFoundError as exc:
        raise HTTPException(status_code=404, detail=exc.message) from exc
    return _to_response(dataset)


@router.get("/{dataset_id}/profile", response_model=DatasetProfileResponse)
def profile_dataset(
    dataset_id: str,
    repo: DatasetRepository = Depends(get_dataset_repository),  # noqa: B008
    loader: DatasetLoader = Depends(get_dataset_loader),  # noqa: B008
) -> DatasetProfileResponse:
    try:
        profile = ProfileDatasetUseCase(repository=repo, loader=loader).execute(
            dataset_id
        )
    except DatasetNotFoundError as exc:
        raise HTTPException(status_code=404, detail=exc.message) from exc
    except FileLoadError as exc:
        raise HTTPException(status_code=422, detail=exc.message) from exc
    return DatasetProfileResponse(
        dataset_id=profile.dataset_id,
        row_count=profile.row_count,
        column_count=profile.column_count,
        columns=[
            ColumnProfileResponse(
                name=c.name, dtype=c.dtype, null_count=c.null_count,
                unique_count=c.unique_count,
            )
            for c in profile.columns
        ],
    )


@router.get(
    "/{dataset_id}/insights", response_model=DatasetInsightReportResponse
)
def dataset_insights(
    dataset_id: str,
    repo: DatasetRepository = Depends(get_dataset_repository),  # noqa: B008
    loader: DatasetLoader = Depends(get_dataset_loader),  # noqa: B008
) -> DatasetInsightReportResponse:
    try:
        report = GenerateDatasetInsightsUseCase(
            repository=repo, loader=loader
        ).execute(dataset_id)
    except DatasetNotFoundError as exc:
        raise HTTPException(status_code=404, detail=exc.message) from exc
    except FileLoadError as exc:
        raise HTTPException(status_code=422, detail=exc.message) from exc
    return DatasetInsightReportResponse(
        dataset_id=report.dataset_id,
        summary=report.summary,
        insights=[
            InsightResponse(category=i.category, message=i.message)
            for i in report.insights
        ],
        warnings=report.warnings,
    )


@router.get(
    "/{dataset_id}/visualizations", response_model=DatasetVisualizationResponse
)
def dataset_visualizations(
    dataset_id: str,
    repo: DatasetRepository = Depends(get_dataset_repository),  # noqa: B008
    chart_gen: ChartGenerator = Depends(get_chart_generator),  # noqa: B008
) -> DatasetVisualizationResponse:
    try:
        viz = GenerateDatasetVisualizationsUseCase(
            repository=repo, chart_generator=chart_gen
        ).execute(dataset_id)
    except DatasetNotFoundError as exc:
        raise HTTPException(status_code=404, detail=exc.message) from exc
    except ChartGenerationError as exc:
        raise HTTPException(status_code=422, detail=exc.message) from exc
    return DatasetVisualizationResponse(
        dataset_id=viz.dataset_id,
        charts=[
            ChartResultResponse(
                chart_type=c.chart_type,
                title=c.title,
                columns=list(c.columns),
                image_base64=c.image_base64,
            )
            for c in viz.charts
        ],
    )


@router.post("/{dataset_id}/query", response_model=AnalyticalAnswerResponse)
def query_dataset(
    dataset_id: str,
    body: AnalyticalQueryRequest,
    repo: DatasetRepository = Depends(get_dataset_repository),  # noqa: B008
    loader: DatasetLoader = Depends(get_dataset_loader),  # noqa: B008
) -> AnalyticalAnswerResponse:
    try:
        answer = AnswerAnalyticalQueryUseCase(
            repository=repo, loader=loader
        ).execute(dataset_id, body.question)
    except DatasetNotFoundError as exc:
        raise HTTPException(status_code=404, detail=exc.message) from exc
    except FileLoadError as exc:
        raise HTTPException(status_code=422, detail=exc.message) from exc
    return AnalyticalAnswerResponse(
        dataset_id=answer.dataset_id,
        intent=answer.intent,
        question=answer.question,
        answer=answer.answer,
        supporting_data=answer.supporting_data,
    )


@router.post(
    "/{dataset_id}/executive-summary", response_model=ExecutiveSummaryResponse
)
def executive_summary(
    dataset_id: str,
    body: ExecutiveSummaryRequest,
    repo: DatasetRepository = Depends(get_dataset_repository),  # noqa: B008
    loader: DatasetLoader = Depends(get_dataset_loader),  # noqa: B008
    llm: LlmClient = Depends(get_llm_client),  # noqa: B008
) -> ExecutiveSummaryResponse:
    try:
        result = GenerateExecutiveSummaryUseCase(
            repository=repo, loader=loader, llm_client=llm
        ).execute(
            dataset_id=dataset_id,
            audience=body.audience,
            tone=body.tone,
            max_paragraphs=body.max_paragraphs,
        )
    except DatasetNotFoundError as exc:
        raise HTTPException(status_code=404, detail=exc.message) from exc
    except FileLoadError as exc:
        raise HTTPException(status_code=422, detail=exc.message) from exc
    except LlmConfigurationError as exc:
        raise HTTPException(status_code=503, detail=exc.message) from exc
    except LlmGenerationError as exc:
        raise HTTPException(status_code=502, detail=exc.message) from exc
    return ExecutiveSummaryResponse(
        dataset_id=result.dataset_id,
        audience=result.audience,
        tone=result.tone,
        content=result.content,
    )


@router.post("/{dataset_id}/rag-query", response_model=RagQueryResponse)
def rag_query(
    dataset_id: str,
    body: RagQueryRequest,
    repo: DatasetRepository = Depends(get_dataset_repository),  # noqa: B008
    loader: DatasetLoader = Depends(get_dataset_loader),  # noqa: B008
    retriever: DocumentRetriever = Depends(get_document_retriever),  # noqa: B008
    llm: LlmClient = Depends(get_llm_client),  # noqa: B008
) -> RagQueryResponse:
    try:
        result = RagQueryUseCase(
            repository=repo, loader=loader, retriever=retriever, llm_client=llm
        ).execute(
            dataset_id=dataset_id, question=body.question, top_k=body.top_k,
        )
    except DatasetNotFoundError as exc:
        raise HTTPException(status_code=404, detail=exc.message) from exc
    except FileLoadError as exc:
        raise HTTPException(status_code=422, detail=exc.message) from exc
    except LlmConfigurationError as exc:
        raise HTTPException(status_code=503, detail=exc.message) from exc
    except (LlmGenerationError, EmbeddingGenerationError) as exc:
        raise HTTPException(status_code=502, detail=exc.message) from exc
    except EmbeddingConfigurationError as exc:
        raise HTTPException(status_code=503, detail=exc.message) from exc
    return RagQueryResponse(
        dataset_id=result.dataset_id,
        question=result.question,
        answer=result.answer,
        sources=[
            DocumentChunkResponse(
                source=c.source, content=c.content, chunk_index=c.chunk_index,
            )
            for c in result.sources
        ],
    )


@router.post(
    "/{dataset_id}/enriched-summary", response_model=ExecutiveSummaryResponse
)
def enriched_summary(
    dataset_id: str,
    body: ExecutiveSummaryRequest,
    repo: DatasetRepository = Depends(get_dataset_repository),  # noqa: B008
    loader: DatasetLoader = Depends(get_dataset_loader),  # noqa: B008
    retriever: DocumentRetriever = Depends(get_document_retriever),  # noqa: B008
    llm: LlmClient = Depends(get_llm_client),  # noqa: B008
) -> ExecutiveSummaryResponse:
    try:
        result = GenerateEnrichedSummaryUseCase(
            repository=repo, loader=loader, retriever=retriever, llm_client=llm
        ).execute(
            dataset_id=dataset_id,
            audience=body.audience,
            tone=body.tone,
            max_paragraphs=body.max_paragraphs,
        )
    except DatasetNotFoundError as exc:
        raise HTTPException(status_code=404, detail=exc.message) from exc
    except FileLoadError as exc:
        raise HTTPException(status_code=422, detail=exc.message) from exc
    except LlmConfigurationError as exc:
        raise HTTPException(status_code=503, detail=exc.message) from exc
    except (LlmGenerationError, EmbeddingGenerationError) as exc:
        raise HTTPException(status_code=502, detail=exc.message) from exc
    except EmbeddingConfigurationError as exc:
        raise HTTPException(status_code=503, detail=exc.message) from exc
    return ExecutiveSummaryResponse(
        dataset_id=result.dataset_id,
        audience=result.audience,
        tone=result.tone,
        content=result.content,
    )
