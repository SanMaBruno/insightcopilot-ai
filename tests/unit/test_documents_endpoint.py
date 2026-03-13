from __future__ import annotations

import tempfile

from fastapi.testclient import TestClient

from src.domain.repositories.document_indexer import DocumentIndexer
from src.infrastructure.files.local_file_storage import LocalFileStorage
from src.presentation.api.app import create_app
from src.presentation.api.dependencies import get_document_indexer, get_file_storage


class _FakeIndexer(DocumentIndexer):

    def __init__(self) -> None:
        self.indexed: list[tuple[str, list[str]]] = []

    def index(self, source: str, chunks: list[str]) -> int:
        self.indexed.append((source, chunks))
        return len(chunks)


def _create_test_client() -> tuple[TestClient, _FakeIndexer, str]:
    app = create_app()
    tmp_dir = tempfile.mkdtemp()
    storage = LocalFileStorage(base_dir=tmp_dir)
    indexer = _FakeIndexer()
    app.dependency_overrides[get_file_storage] = lambda: storage
    app.dependency_overrides[get_document_indexer] = lambda: indexer
    return TestClient(app), indexer, tmp_dir


class TestUploadDocumentEndpoint:

    def setup_method(self) -> None:
        self.client, self.indexer, self.tmp_dir = _create_test_client()

    def test_upload_txt_returns_201(self) -> None:
        response = self.client.post(
            "/documents/upload",
            files={"file": ("glosario.txt", b"Contenido del glosario", "text/plain")},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["source"] == "glosario.txt"
        assert "file_path" in data

    def test_upload_md_returns_201(self) -> None:
        response = self.client.post(
            "/documents/upload",
            files={"file": ("contexto.md", b"# Contexto\nDatos Q1", "text/plain")},
        )

        assert response.status_code == 201
        assert response.json()["source"] == "contexto.md"

    def test_upload_rejects_non_allowed_extension(self) -> None:
        response = self.client.post(
            "/documents/upload",
            files={"file": ("data.pdf", b"pdf content", "application/pdf")},
        )

        assert response.status_code == 400
        assert ".md" in response.json()["detail"]
        assert ".txt" in response.json()["detail"]

    def test_upload_rejects_empty_file(self) -> None:
        response = self.client.post(
            "/documents/upload",
            files={"file": ("empty.txt", b"", "text/plain")},
        )

        assert response.status_code == 400
        assert "vacío" in response.json()["detail"]


class TestIndexDocumentEndpoint:

    def setup_method(self) -> None:
        self.client, self.indexer, self.tmp_dir = _create_test_client()

    def test_index_uploaded_document(self) -> None:
        # Primero subimos
        upload = self.client.post(
            "/documents/upload",
            files={"file": ("doc.txt", b"Contenido para indexar", "text/plain")},
        ).json()

        # Luego indexamos
        response = self.client.post(
            "/documents/index",
            json={"file_path": upload["file_path"]},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["chunks_indexed"] >= 1
        assert "source" in data

    def test_index_nonexistent_file_returns_404(self) -> None:
        response = self.client.post(
            "/documents/index",
            json={"file_path": "/nonexistent/file.txt"},
        )

        assert response.status_code == 404
        assert "no encontrado" in response.json()["detail"]

    def test_index_respects_chunk_size(self) -> None:
        # Subimos un documento largo
        content = ("Línea de prueba.\n" * 100).encode()
        upload = self.client.post(
            "/documents/upload",
            files={"file": ("largo.txt", content, "text/plain")},
        ).json()

        response = self.client.post(
            "/documents/index",
            json={"file_path": upload["file_path"], "chunk_size": 200, "overlap": 20},
        )

        assert response.status_code == 200
        assert response.json()["chunks_indexed"] >= 2
