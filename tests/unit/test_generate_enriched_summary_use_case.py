from __future__ import annotations

import os

import pytest

from src.application.use_cases.generate_enriched_summary_use_case import (
    GenerateEnrichedSummaryUseCase,
)
from src.application.use_cases.get_dataset_by_id_use_case import DatasetNotFoundError
from src.domain.llm_client import LlmClient
from src.domain.repositories.document_retriever import DocumentRetriever
from src.domain.value_objects.document_chunk import DocumentChunk
from src.infrastructure.files.csv_dataset_loader import CsvDatasetLoader
from src.infrastructure.persistence.in_memory_dataset_repository import (
    InMemoryDatasetRepository,
)

_CSV_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "data", "sample", "test_data.csv")
)


class _FakeLlmClient(LlmClient):
    def __init__(self, response: str = "Resumen enriquecido de prueba.") -> None:
        self._response = response
        self.last_user_prompt: str | None = None

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        self.last_user_prompt = user_prompt
        return self._response


class _FakeRetriever(DocumentRetriever):
    def __init__(self) -> None:
        self._chunks = [
            DocumentChunk(source="contexto.md", content="Datos del Q1 2024", chunk_index=0),
        ]

    def retrieve(self, query: str, top_k: int = 5) -> list[DocumentChunk]:
        return self._chunks[:top_k]


class TestGenerateEnrichedSummaryUseCase:

    def setup_method(self) -> None:
        self.repo = InMemoryDatasetRepository()
        self.loader = CsvDatasetLoader()
        self.llm = _FakeLlmClient()
        self.retriever = _FakeRetriever()
        self.use_case = GenerateEnrichedSummaryUseCase(
            repository=self.repo,
            loader=self.loader,
            retriever=self.retriever,
            llm_client=self.llm,
        )

    def _create_dataset(self) -> str:
        from src.application.use_cases.create_dataset_use_case import CreateDatasetUseCase

        ds = CreateDatasetUseCase(repository=self.repo).execute(
            name="test", file_path=_CSV_PATH, source_type="csv",
        )
        return ds.id

    def test_returns_enriched_summary(self) -> None:
        ds_id = self._create_dataset()

        result = self.use_case.execute(ds_id)

        assert result.dataset_id == ds_id
        assert result.content == "Resumen enriquecido de prueba."
        assert result.audience == "equipo técnico"
        assert result.tone == "profesional"

    def test_prompt_includes_document_context(self) -> None:
        ds_id = self._create_dataset()

        self.use_case.execute(ds_id)

        assert self.llm.last_user_prompt is not None
        assert "contexto.md" in self.llm.last_user_prompt
        assert "Datos del Q1 2024" in self.llm.last_user_prompt

    def test_passes_audience_and_tone(self) -> None:
        ds_id = self._create_dataset()

        result = self.use_case.execute(
            ds_id, audience="directivos", tone="ejecutivo", max_paragraphs=5,
        )

        assert result.audience == "directivos"
        assert result.tone == "ejecutivo"

    def test_raises_when_dataset_not_found(self) -> None:
        with pytest.raises(DatasetNotFoundError):
            self.use_case.execute("nonexistent")
