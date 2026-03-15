from __future__ import annotations

from src.domain.llm_client import LlmClient
from src.domain.repositories.chart_generator import ChartGenerator
from src.domain.repositories.dataset_loader import DatasetLoader
from src.domain.repositories.dataset_repository import DatasetRepository
from src.domain.repositories.document_indexer import DocumentIndexer
from src.domain.repositories.document_retriever import DocumentRetriever
from src.domain.repositories.curated_result_repository import CuratedResultRepository
from src.domain.repositories.file_storage import FileStorage
from src.domain.repositories.transformation_engine import TransformationEngine
from src.infrastructure.etl.pandas_transformation_engine import PandasTransformationEngine
from src.infrastructure.files.csv_dataset_loader import CsvDatasetLoader
from src.infrastructure.files.local_file_storage import LocalFileStorage
from src.infrastructure.files.matplotlib_chart_generator import MatplotlibChartGenerator
from src.infrastructure.llm.gemini_llm_client import GeminiLlmClient
from src.infrastructure.llm.mock_llm_client import MockLlmClient
from src.infrastructure.llm.ollama_llm_client import OllamaLlmClient
from src.infrastructure.llm.openai_llm_client import OpenAiLlmClient
from src.infrastructure.persistence.in_memory_curated_result_repository import (
    InMemoryCuratedResultRepository,
)
from src.infrastructure.persistence.sqlite_dataset_repository import (
    SqliteDatasetRepository,
)
from src.infrastructure.rag.embedding_function import EmbeddingFunction
from src.infrastructure.rag.gemini_embedding_function import GeminiEmbeddingFunction
from src.infrastructure.rag.in_memory_vector_store import InMemoryVectorStore
from src.infrastructure.rag.mock_embedding_function import MockEmbeddingFunction
from src.infrastructure.rag.openai_embedding_function import OpenAiEmbeddingFunction
from src.shared.config.settings import settings
from src.shared.config.settings import Settings

_dataset_repository = SqliteDatasetRepository(db_path=settings.database_url)
_dataset_loader = CsvDatasetLoader()
_chart_generator = MatplotlibChartGenerator()
_file_storage = LocalFileStorage(base_dir=settings.upload_dir)
_curated_file_storage = LocalFileStorage(base_dir=settings.curated_dir)
_transformation_engine = PandasTransformationEngine()
_curated_result_repository = InMemoryCuratedResultRepository()


def build_embedding_function(config: Settings) -> EmbeddingFunction:
    """Construye el proveedor de embeddings según EMBEDDING_MODE."""
    if config.embedding_mode == "mock" or config.embedding_mode == "local":
        return MockEmbeddingFunction()
    if config.embedding_mode == "gemini":
        return GeminiEmbeddingFunction(
            api_key=config.gemini_api_key, model=config.embedding_model,
        )
    return OpenAiEmbeddingFunction(
        api_key=config.openai_api_key, model=config.embedding_model,
    )


def build_vector_store(config: Settings) -> InMemoryVectorStore:
    embed_fn = build_embedding_function(config)
    return InMemoryVectorStore(embed_fn=embed_fn)


def build_llm_client(config: Settings) -> LlmClient:
    """Construye el cliente LLM según LLM_MODE."""
    if config.llm_mode == "mock":
        return MockLlmClient()
    if config.llm_mode == "gemini":
        return GeminiLlmClient(
            api_key=config.gemini_api_key, model=config.gemini_model,
        )
    if config.llm_mode == "ollama":
        return OllamaLlmClient(
            base_url=config.ollama_base_url, model=config.ollama_model,
        )
    return OpenAiLlmClient(
        api_key=config.openai_api_key, model=config.openai_model,
    )


_vector_store: InMemoryVectorStore | None = None


def _get_vector_store() -> InMemoryVectorStore:
    global _vector_store
    if _vector_store is None:
        _vector_store = build_vector_store(settings)
    return _vector_store


_llm_client: LlmClient | None = None


def get_dataset_repository() -> DatasetRepository:
    return _dataset_repository


def get_dataset_loader() -> DatasetLoader:
    return _dataset_loader


def get_chart_generator() -> ChartGenerator:
    return _chart_generator


def get_file_storage() -> FileStorage:
    return _file_storage


def get_curated_file_storage() -> FileStorage:
    return _curated_file_storage


def get_transformation_engine() -> TransformationEngine:
    return _transformation_engine


def get_curated_result_repository() -> CuratedResultRepository:
    return _curated_result_repository


def get_llm_client() -> LlmClient:
    global _llm_client
    if _llm_client is None:
        _llm_client = build_llm_client(settings)
    return _llm_client


def get_document_indexer() -> DocumentIndexer:
    return _get_vector_store()


def get_document_retriever() -> DocumentRetriever:
    return _get_vector_store()
