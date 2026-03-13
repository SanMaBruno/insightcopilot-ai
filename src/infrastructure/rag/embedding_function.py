from __future__ import annotations

from typing import Protocol


class EmbeddingFunction(Protocol):
    """Protocolo para generar embeddings a partir de textos."""

    def __call__(self, texts: list[str]) -> list[list[float]]:
        ...
