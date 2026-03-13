from __future__ import annotations

from src.application.services.text_chunker import chunk_text
from src.domain.repositories.document_indexer import DocumentIndexer


class IndexDocumentUseCase:

    def __init__(self, indexer: DocumentIndexer) -> None:
        self._indexer = indexer

    def execute(
        self,
        source: str,
        content: str,
        chunk_size: int = 500,
        overlap: int = 50,
    ) -> int:
        """Lee contenido de texto, lo fragmenta e indexa. Retorna cantidad de chunks."""
        chunks = chunk_text(content, chunk_size=chunk_size, overlap=overlap)
        return self._indexer.index(source, chunks)
