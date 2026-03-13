from __future__ import annotations

import os

import pytest

from src.application.use_cases.get_dataset_by_id_use_case import DatasetNotFoundError
from src.application.use_cases.rag_query_use_case import RagQueryUseCase
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
    def __init__(self, response: str = "Respuesta RAG de prueba.") -> None:
        self._response = response
        self.last_system_prompt: str | None = None
        self.last_user_prompt: str | None = None

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        self.last_system_prompt = system_prompt
        self.last_user_prompt = user_prompt
        return self._response


class _FakeRetriever(DocumentRetriever):
    def __init__(self, chunks: list[DocumentChunk] | None = None) -> None:
        self._chunks = chunks if chunks is not None else [
            DocumentChunk(source="glosario.md", content="Definición de edad: años.", chunk_index=0),
        ]

    def retrieve(self, query: str, top_k: int = 5) -> list[DocumentChunk]:
        return self._chunks[:top_k]


class TestRagQueryUseCase:

    def setup_method(self) -> None:
        self.repo = InMemoryDatasetRepository()
        self.loader = CsvDatasetLoader()
        self.llm = _FakeLlmClient()
        self.retriever = _FakeRetriever()
        self.use_case = RagQueryUseCase(
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

    def test_returns_contextual_answer(self) -> None:
        ds_id = self._create_dataset()

        result = self.use_case.execute(ds_id, "¿Qué es la edad?")

        assert result.dataset_id == ds_id
        assert result.question == "¿Qué es la edad?"
        assert result.answer == "Respuesta RAG de prueba."

    def test_includes_document_sources(self) -> None:
        ds_id = self._create_dataset()

        result = self.use_case.execute(ds_id, "¿Qué es la edad?")

        assert len(result.sources) == 1
        assert result.sources[0].source == "glosario.md"

    def test_prompt_includes_question_and_context(self) -> None:
        ds_id = self._create_dataset()

        self.use_case.execute(ds_id, "¿Cuántos registros hay?")

        assert self.llm.last_user_prompt is not None
        assert "¿Cuántos registros hay?" in self.llm.last_user_prompt
        assert "test" in self.llm.last_user_prompt  # dataset name
        assert "glosario.md" in self.llm.last_user_prompt  # document chunk source

    def test_system_prompt_includes_guardrails(self) -> None:
        ds_id = self._create_dataset()

        self.use_case.execute(ds_id, "pregunta")

        assert self.llm.last_system_prompt is not None
        assert "ÚNICAMENTE" in self.llm.last_system_prompt

    def test_raises_when_dataset_not_found(self) -> None:
        with pytest.raises(DatasetNotFoundError):
            self.use_case.execute("nonexistent", "pregunta")

    def test_works_with_no_document_chunks(self) -> None:
        retriever = _FakeRetriever(chunks=[])
        use_case = RagQueryUseCase(
            repository=self.repo,
            loader=self.loader,
            retriever=retriever,
            llm_client=self.llm,
        )
        ds_id = self._create_dataset()

        result = use_case.execute(ds_id, "pregunta sin contexto documental")

        assert result.sources == []
        assert result.answer == "Respuesta RAG de prueba."

    def test_respects_top_k(self) -> None:
        many_chunks = [
            DocumentChunk(source=f"doc{i}.txt", content=f"chunk {i}", chunk_index=0)
            for i in range(10)
        ]
        retriever = _FakeRetriever(chunks=many_chunks)
        use_case = RagQueryUseCase(
            repository=self.repo,
            loader=self.loader,
            retriever=retriever,
            llm_client=self.llm,
        )
        ds_id = self._create_dataset()

        result = use_case.execute(ds_id, "query", top_k=3)

        assert len(result.sources) == 3
