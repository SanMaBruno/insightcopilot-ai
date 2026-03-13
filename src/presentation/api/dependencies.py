from __future__ import annotations

from src.domain.llm_client import LlmClient
from src.domain.repositories.chart_generator import ChartGenerator
from src.domain.repositories.dataset_loader import DatasetLoader
from src.domain.repositories.dataset_repository import DatasetRepository
from src.domain.repositories.document_indexer import DocumentIndexer
from src.domain.repositories.document_retriever import DocumentRetriever
from src.domain.repositories.file_storage import FileStorage
from src.infrastructure.files.csv_dataset_loader import CsvDatasetLoader
from src.infrastructure.files.local_file_storage import LocalFileStorage
from src.infrastructure.files.matplotlib_chart_generator import MatplotlibChartGenerator
from src.infrastructure.llm.openai_llm_client import OpenAiLlmClient
from src.infrastructure.persistence.sqlite_dataset_repository import (
    SqliteDatasetRepository,
)
from src.infrastructure.rag.in_memory_vector_store import InMemoryVectorStore
from src.infrastructure.rag.openai_embedding_function import OpenAiEmbeddingFunction
from src.shared.config.settings import settings

_dataset_repository = SqliteDatasetRepository(db_path=settings.database_url)
_dataset_loader = CsvDatasetLoader()
_chart_generator = MatplotlibChartGenerator()
_file_storage = LocalFileStorage(base_dir=settings.upload_dir)


def _create_vector_store() -> InMemoryVectorStore:
    embed_fn = OpenAiEmbeddingFunction(
        api_key=settings.openai_api_key, model=settings.embedding_model,
    )
    return InMemoryVectorStore(embed_fn=embed_fn)


_vector_store: InMemoryVectorStore | None = None


def _get_vector_store() -> InMemoryVectorStore:
    global _vector_store
    if _vector_store is None:
        _vector_store = _create_vector_store()
    return _vector_store


_llm_client = OpenAiLlmClient(
    api_key=settings.openai_api_key, model=settings.openai_model
)


def get_dataset_repository() -> DatasetRepository:
    return _dataset_repository


def get_dataset_loader() -> DatasetLoader:
    return _dataset_loader


def get_chart_generator() -> ChartGenerator:
    return _chart_generator


def get_file_storage() -> FileStorage:
    return _file_storage


def get_llm_client() -> LlmClient:
    return _llm_client


def get_document_indexer() -> DocumentIndexer:
    return _get_vector_store()


def get_document_retriever() -> DocumentRetriever:
    return _get_vector_store()
