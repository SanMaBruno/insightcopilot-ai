from __future__ import annotations

from src.domain.value_objects.document_chunk import DocumentChunk
from src.infrastructure.rag.in_memory_vector_store import InMemoryVectorStore


def _fake_embed_fn(texts: list[str]) -> list[list[float]]:
    """Embedding determinista: usa la longitud del texto como única dimensión."""
    return [[float(len(t)), float(len(t) % 10)] for t in texts]


def _semantic_embed_fn(texts: list[str]) -> list[list[float]]:
    """Embedding fake que asigna direcciones distintas por palabras clave."""
    result: list[list[float]] = []
    for t in texts:
        lower = t.lower()
        if "ventas" in lower or "revenue" in lower:
            result.append([1.0, 0.0, 0.0])
        elif "cliente" in lower or "customer" in lower:
            result.append([0.0, 1.0, 0.0])
        elif "producto" in lower or "product" in lower:
            result.append([0.0, 0.0, 1.0])
        else:
            result.append([0.3, 0.3, 0.3])
    return result


class TestInMemoryVectorStoreIndex:

    def test_index_returns_chunk_count(self) -> None:
        store = InMemoryVectorStore(embed_fn=_fake_embed_fn)

        count = store.index("doc.txt", ["chunk 1", "chunk 2", "chunk 3"])

        assert count == 3

    def test_index_empty_list_returns_zero(self) -> None:
        store = InMemoryVectorStore(embed_fn=_fake_embed_fn)

        assert store.index("doc.txt", []) == 0

    def test_index_multiple_documents(self) -> None:
        store = InMemoryVectorStore(embed_fn=_fake_embed_fn)

        store.index("a.txt", ["chunk a1", "chunk a2"])
        store.index("b.txt", ["chunk b1"])

        # Debería tener 3 chunks en total
        results = store.retrieve("any query", top_k=10)
        assert len(results) == 3


class TestInMemoryVectorStoreRetrieve:

    def test_retrieve_returns_empty_when_no_documents(self) -> None:
        store = InMemoryVectorStore(embed_fn=_fake_embed_fn)

        results = store.retrieve("test query")

        assert results == []

    def test_retrieve_returns_document_chunks(self) -> None:
        store = InMemoryVectorStore(embed_fn=_fake_embed_fn)
        store.index("doc.txt", ["contenido del chunk"])

        results = store.retrieve("query")

        assert len(results) == 1
        assert isinstance(results[0], DocumentChunk)
        assert results[0].source == "doc.txt"
        assert results[0].content == "contenido del chunk"
        assert results[0].chunk_index == 0

    def test_retrieve_respects_top_k(self) -> None:
        store = InMemoryVectorStore(embed_fn=_fake_embed_fn)
        store.index("doc.txt", [f"chunk {i}" for i in range(10)])

        results = store.retrieve("query", top_k=3)

        assert len(results) == 3

    def test_retrieve_ranks_by_similarity(self) -> None:
        store = InMemoryVectorStore(embed_fn=_semantic_embed_fn)
        store.index("ventas.md", ["Informe de ventas y revenue del Q1"])
        store.index("clientes.md", ["Listado de clientes activos"])
        store.index("productos.md", ["Catálogo de productos disponibles"])

        results = store.retrieve("¿Cuáles son las ventas?", top_k=3)

        # El chunk sobre ventas debería ser el más relevante
        assert results[0].source == "ventas.md"

    def test_retrieve_preserves_chunk_index(self) -> None:
        store = InMemoryVectorStore(embed_fn=_fake_embed_fn)
        store.index("doc.txt", ["primero", "segundo", "tercero"])

        results = store.retrieve("query", top_k=10)

        indices = {r.chunk_index for r in results}
        assert indices == {0, 1, 2}


class TestCosinesSimilarity:

    def test_identical_vectors(self) -> None:
        sim = InMemoryVectorStore._cosine_similarity([1.0, 0.0], [1.0, 0.0])
        assert abs(sim - 1.0) < 1e-6

    def test_orthogonal_vectors(self) -> None:
        sim = InMemoryVectorStore._cosine_similarity([1.0, 0.0], [0.0, 1.0])
        assert abs(sim) < 1e-6

    def test_zero_vector(self) -> None:
        sim = InMemoryVectorStore._cosine_similarity([0.0, 0.0], [1.0, 1.0])
        assert sim == 0.0
