from __future__ import annotations

import hashlib
import math


class MockEmbeddingFunction:
    """Embeddings determinísticos para demos locales."""

    def __init__(self, dimensions: int = 16) -> None:
        self._dimensions = dimensions

    def __call__(self, texts: list[str]) -> list[list[float]]:
        return [self._embed(text) for text in texts]

    def _embed(self, text: str) -> list[float]:
        vector = [0.0] * self._dimensions
        tokens = text.lower().split()
        if not tokens:
            return vector

        for token in tokens:
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            index = digest[0] % self._dimensions
            weight = 1 + (digest[1] / 255)
            vector[index] += weight

        norm = math.sqrt(sum(value * value for value in vector))
        if norm == 0:
            return vector
        return [value / norm for value in vector]
