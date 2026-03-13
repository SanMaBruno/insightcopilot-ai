from __future__ import annotations

from src.application.use_cases.index_document_use_case import IndexDocumentUseCase
from src.domain.repositories.document_indexer import DocumentIndexer


class _FakeIndexer(DocumentIndexer):

    def __init__(self) -> None:
        self.indexed: list[tuple[str, list[str]]] = []

    def index(self, source: str, chunks: list[str]) -> int:
        self.indexed.append((source, chunks))
        return len(chunks)


class TestIndexDocumentUseCase:

    def test_indexes_text_and_returns_count(self) -> None:
        indexer = _FakeIndexer()
        use_case = IndexDocumentUseCase(indexer=indexer)

        count = use_case.execute(
            source="doc.txt",
            content="Línea uno\nLínea dos\nLínea tres\n" * 50,
            chunk_size=100,
            overlap=10,
        )

        assert count > 0
        assert len(indexer.indexed) == 1
        assert indexer.indexed[0][0] == "doc.txt"

    def test_empty_content_returns_zero(self) -> None:
        indexer = _FakeIndexer()
        use_case = IndexDocumentUseCase(indexer=indexer)

        count = use_case.execute(source="empty.txt", content="  ")

        assert count == 0

    def test_passes_chunks_to_indexer(self) -> None:
        indexer = _FakeIndexer()
        use_case = IndexDocumentUseCase(indexer=indexer)

        use_case.execute(source="test.md", content="Contenido de prueba")

        assert len(indexer.indexed) == 1
        source, chunks = indexer.indexed[0]
        assert source == "test.md"
        assert len(chunks) == 1
        assert "Contenido de prueba" in chunks[0]
