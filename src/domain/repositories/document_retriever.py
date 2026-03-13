from __future__ import annotations

from abc import ABC, abstractmethod

from src.domain.value_objects.document_chunk import DocumentChunk


class DocumentRetriever(ABC):

    @abstractmethod
    def retrieve(self, query: str, top_k: int = 5) -> list[DocumentChunk]:
        """Recupera los fragmentos más relevantes para una consulta."""
        ...
