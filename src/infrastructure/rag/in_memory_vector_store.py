from __future__ import annotations

import math

from src.domain.repositories.document_indexer import DocumentIndexer
from src.domain.repositories.document_retriever import DocumentRetriever
from src.domain.value_objects.document_chunk import DocumentChunk
from src.infrastructure.rag.embedding_function import EmbeddingFunction


class InMemoryVectorStore(DocumentIndexer, DocumentRetriever):
    """Almacén vectorial en memoria que implementa indexación y recuperación."""

    def __init__(self, embed_fn: EmbeddingFunction) -> None:
        self._embed_fn = embed_fn
        self._chunks: list[DocumentChunk] = []
        self._embeddings: list[list[float]] = []

    # --- DocumentIndexer ---

    def index(self, source: str, chunks: list[str]) -> int:
        if not chunks:
            return 0
        doc_chunks = [
            DocumentChunk(source=source, content=text, chunk_index=i)
            for i, text in enumerate(chunks)
        ]
        embeddings = self._embed_fn([c.content for c in doc_chunks])
        self._chunks.extend(doc_chunks)
        self._embeddings.extend(embeddings)
        return len(doc_chunks)

    # --- DocumentRetriever ---

    def retrieve(self, query: str, top_k: int = 5) -> list[DocumentChunk]:
        if not self._chunks:
            return []
        query_embedding = self._embed_fn([query])[0]
        scored = [
            (self._cosine_similarity(query_embedding, emb), chunk)
            for chunk, emb in zip(self._chunks, self._embeddings)
        ]
        scored.sort(key=lambda pair: pair[0], reverse=True)
        return [chunk for _, chunk in scored[:top_k]]

    # --- Utilidades internas ---

    @staticmethod
    def _cosine_similarity(a: list[float], b: list[float]) -> float:
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(x * x for x in b))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)
