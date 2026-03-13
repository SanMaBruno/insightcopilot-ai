from __future__ import annotations

from abc import ABC, abstractmethod


class DocumentIndexer(ABC):

    @abstractmethod
    def index(self, source: str, chunks: list[str]) -> int:
        """Indexa fragmentos de texto de un documento. Retorna la cantidad indexada."""
        ...
