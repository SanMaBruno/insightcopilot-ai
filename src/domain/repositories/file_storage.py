from __future__ import annotations

from abc import ABC, abstractmethod


class FileStorage(ABC):

    @abstractmethod
    def save(self, filename: str, content: bytes) -> str:
        """Guarda contenido binario y retorna la ruta absoluta del archivo."""
        ...
