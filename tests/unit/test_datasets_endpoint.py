from fastapi.testclient import TestClient

from src.domain.llm_client import LlmClient
from src.domain.repositories.document_retriever import DocumentRetriever
from src.domain.value_objects.document_chunk import DocumentChunk
from src.infrastructure.persistence.in_memory_dataset_repository import (
    InMemoryDatasetRepository,
)
from src.presentation.api.app import create_app
from src.presentation.api.dependencies import (
    get_dataset_repository,
    get_document_retriever,
    get_llm_client,
)


def _create_test_client() -> tuple[TestClient, InMemoryDatasetRepository]:
    """Crea un TestClient con un repositorio aislado por test."""
    app = create_app()
    repo = InMemoryDatasetRepository()
    app.dependency_overrides[get_dataset_repository] = lambda: repo
    return TestClient(app), repo


_PAYLOAD = {
    "name": "ventas",
    "file_path": "/data/ventas.csv",
    "source_type": "csv",
}


class TestCreateDatasetEndpoint:

    def setup_method(self) -> None:
        self.client, self.repo = _create_test_client()

    def test_create_dataset_returns_201(self) -> None:
        response = self.client.post("/datasets", json=_PAYLOAD)

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "ventas"
        assert data["file_path"] == "/data/ventas.csv"
        assert data["source_type"] == "csv"
        assert "id" in data
        assert "created_at" in data

    def test_create_dataset_rejects_missing_fields(self) -> None:
        response = self.client.post("/datasets", json={"name": "ventas"})

        assert response.status_code == 422

    def test_create_dataset_returns_unique_ids(self) -> None:
        r1 = self.client.post("/datasets", json=_PAYLOAD)
        r2 = self.client.post("/datasets", json=_PAYLOAD)

        assert r1.json()["id"] != r2.json()["id"]


class TestListDatasetsEndpoint:

    def setup_method(self) -> None:
        self.client, self.repo = _create_test_client()

    def test_list_empty(self) -> None:
        response = self.client.get("/datasets")

        assert response.status_code == 200
        assert response.json() == []

    def test_list_returns_created_datasets(self) -> None:
        self.client.post("/datasets", json=_PAYLOAD)
        self.client.post("/datasets", json={**_PAYLOAD, "name": "clientes"})

        response = self.client.get("/datasets")

        assert response.status_code == 200
        assert len(response.json()) == 2


class TestGetDatasetEndpoint:

    def setup_method(self) -> None:
        self.client, self.repo = _create_test_client()

    def test_get_existing_dataset(self) -> None:
        created = self.client.post("/datasets", json=_PAYLOAD).json()

        response = self.client.get(f"/datasets/{created['id']}")

        assert response.status_code == 200
        assert response.json()["id"] == created["id"]
        assert response.json()["name"] == "ventas"

    def test_get_nonexistent_returns_404(self) -> None:
        response = self.client.get("/datasets/nonexistent")

        assert response.status_code == 404
        assert "no encontrado" in response.json()["detail"]


class TestProfileDatasetEndpoint:

    def setup_method(self) -> None:
        self.client, self.repo = _create_test_client()

    def test_profile_existing_dataset(self) -> None:
        import os

        csv_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "data", "sample", "test_data.csv")
        )
        payload = {"name": "test", "file_path": csv_path, "source_type": "csv"}
        created = self.client.post("/datasets", json=payload).json()

        response = self.client.get(f"/datasets/{created['id']}/profile")

        assert response.status_code == 200
        data = response.json()
        assert data["dataset_id"] == created["id"]
        assert data["row_count"] == 3
        assert data["column_count"] == 3
        assert len(data["columns"]) == 3
        assert data["columns"][0]["name"] == "name"

    def test_profile_nonexistent_dataset_returns_404(self) -> None:
        response = self.client.get("/datasets/nonexistent/profile")

        assert response.status_code == 404

    def test_profile_with_bad_file_returns_422(self) -> None:
        payload = {"name": "bad", "file_path": "/missing.csv", "source_type": "csv"}
        created = self.client.post("/datasets", json=payload).json()

        response = self.client.get(f"/datasets/{created['id']}/profile")

        assert response.status_code == 422
        assert "no encontrado" in response.json()["detail"]


class TestInsightsEndpoint:

    def setup_method(self) -> None:
        self.client, self.repo = _create_test_client()

    def test_insights_existing_dataset(self) -> None:
        import os

        csv_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "data", "sample", "test_data.csv")
        )
        payload = {"name": "test", "file_path": csv_path, "source_type": "csv"}
        created = self.client.post("/datasets", json=payload).json()

        response = self.client.get(f"/datasets/{created['id']}/insights")

        assert response.status_code == 200
        data = response.json()
        assert data["dataset_id"] == created["id"]
        assert "3 filas" in data["summary"]
        assert isinstance(data["insights"], list)
        assert isinstance(data["warnings"], list)
        assert len(data["insights"]) > 0

    def test_insights_nonexistent_returns_404(self) -> None:
        response = self.client.get("/datasets/nonexistent/insights")

        assert response.status_code == 404

    def test_insights_bad_file_returns_422(self) -> None:
        payload = {"name": "bad", "file_path": "/missing.csv", "source_type": "csv"}
        created = self.client.post("/datasets", json=payload).json()

        response = self.client.get(f"/datasets/{created['id']}/insights")

        assert response.status_code == 422


class TestVisualizationsEndpoint:

    def setup_method(self) -> None:
        self.client, self.repo = _create_test_client()

    def test_visualizations_existing_dataset(self) -> None:
        import os

        csv_path = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__), "..", "..", "data", "sample", "test_data.csv"
            )
        )
        payload = {"name": "test", "file_path": csv_path, "source_type": "csv"}
        created = self.client.post("/datasets", json=payload).json()

        response = self.client.get(f"/datasets/{created['id']}/visualizations")

        assert response.status_code == 200
        data = response.json()
        assert data["dataset_id"] == created["id"]
        assert isinstance(data["charts"], list)
        assert len(data["charts"]) >= 3  # dtype_dist + histogram(age) + top_values(name,city)
        chart_types = {c["chart_type"] for c in data["charts"]}
        assert "dtype_distribution" in chart_types
        assert "histogram" in chart_types

    def test_visualizations_nonexistent_returns_404(self) -> None:
        response = self.client.get("/datasets/nonexistent/visualizations")

        assert response.status_code == 404

    def test_visualizations_bad_file_returns_422(self) -> None:
        payload = {"name": "bad", "file_path": "/missing.csv", "source_type": "csv"}
        created = self.client.post("/datasets", json=payload).json()

        response = self.client.get(f"/datasets/{created['id']}/visualizations")

        assert response.status_code == 422


class TestQueryEndpoint:

    def setup_method(self) -> None:
        self.client, self.repo = _create_test_client()

    def _create_with_csv(self) -> dict:
        import os

        csv_path = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__), "..", "..", "data", "sample", "test_data.csv"
            )
        )
        payload = {"name": "test", "file_path": csv_path, "source_type": "csv"}
        return self.client.post("/datasets", json=payload).json()

    def test_query_summary(self) -> None:
        created = self._create_with_csv()

        response = self.client.post(
            f"/datasets/{created['id']}/query",
            json={"question": "Dame un resumen general"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["dataset_id"] == created["id"]
        assert data["intent"] == "resumen"
        assert "3 filas" in data["answer"]
        assert isinstance(data["supporting_data"], list)

    def test_query_nulls(self) -> None:
        created = self._create_with_csv()

        response = self.client.post(
            f"/datasets/{created['id']}/query",
            json={"question": "¿Qué columnas tienen nulos?"},
        )

        assert response.status_code == 200
        assert response.json()["intent"] == "nulos"

    def test_query_unknown_intent(self) -> None:
        created = self._create_with_csv()

        response = self.client.post(
            f"/datasets/{created['id']}/query",
            json={"question": "abc xyz 123"},
        )

        assert response.status_code == 200
        assert response.json()["intent"] == "desconocida"

    def test_query_nonexistent_returns_404(self) -> None:
        response = self.client.post(
            "/datasets/nonexistent/query",
            json={"question": "resumen"},
        )

        assert response.status_code == 404

    def test_query_bad_file_returns_422(self) -> None:
        payload = {"name": "bad", "file_path": "/missing.csv", "source_type": "csv"}
        created = self.client.post("/datasets", json=payload).json()

        response = self.client.post(
            f"/datasets/{created['id']}/query",
            json={"question": "resumen"},
        )

        assert response.status_code == 422


class TestUploadEndpoint:

    def setup_method(self) -> None:
        import tempfile

        from src.infrastructure.files.local_file_storage import LocalFileStorage
        from src.presentation.api.dependencies import get_file_storage

        self._tmp_dir = tempfile.mkdtemp()
        self.client, self.repo = _create_test_client()
        storage = LocalFileStorage(base_dir=self._tmp_dir)
        self.client.app.dependency_overrides[get_file_storage] = lambda: storage  # type: ignore[union-attr]

    def test_upload_csv_returns_201(self) -> None:
        response = self.client.post(
            "/datasets/upload",
            files={"file": ("ventas.csv", b"name,age\nAlice,30\n", "text/csv")},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "ventas"
        assert data["source_type"] == "csv"
        assert data["file_path"].endswith(".csv")
        assert "id" in data

    def test_upload_rejects_non_csv(self) -> None:
        response = self.client.post(
            "/datasets/upload",
            files={"file": ("data.json", b'{"a":1}', "application/json")},
        )

        assert response.status_code == 400
        assert "CSV" in response.json()["detail"]

    def test_upload_rejects_empty_file(self) -> None:
        response = self.client.post(
            "/datasets/upload",
            files={"file": ("empty.csv", b"", "text/csv")},
        )

        assert response.status_code == 400
        assert "vacío" in response.json()["detail"]

    def test_uploaded_dataset_is_listable(self) -> None:
        self.client.post(
            "/datasets/upload",
            files={"file": ("test.csv", b"a,b\n1,2\n", "text/csv")},
        )

        response = self.client.get("/datasets")
        assert len(response.json()) == 1

    def test_uploaded_csv_is_profilable(self) -> None:
        upload = self.client.post(
            "/datasets/upload",
            files={"file": ("test.csv", b"name,age\nAlice,30\nBob,25\n", "text/csv")},
        ).json()

        response = self.client.get(f"/datasets/{upload['id']}/profile")

        assert response.status_code == 200
        assert response.json()["row_count"] == 2


class _FakeLlmClient(LlmClient):
    def generate(self, system_prompt: str, user_prompt: str) -> str:
        return "Resumen ejecutivo de prueba."


class TestExecutiveSummaryEndpoint:

    def setup_method(self) -> None:
        self.client, self.repo = _create_test_client()
        self.client.app.dependency_overrides[get_llm_client] = lambda: _FakeLlmClient()  # type: ignore[union-attr]

    def _create_with_csv(self) -> dict:
        import os

        csv_path = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__), "..", "..", "data", "sample", "test_data.csv"
            )
        )
        payload = {"name": "test", "file_path": csv_path, "source_type": "csv"}
        return self.client.post("/datasets", json=payload).json()

    def test_executive_summary_returns_200(self) -> None:
        created = self._create_with_csv()

        response = self.client.post(
            f"/datasets/{created['id']}/executive-summary",
            json={"audience": "directivos", "tone": "ejecutivo", "max_paragraphs": 2},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["dataset_id"] == created["id"]
        assert data["audience"] == "directivos"
        assert data["tone"] == "ejecutivo"
        assert data["content"] == "Resumen ejecutivo de prueba."

    def test_executive_summary_uses_defaults(self) -> None:
        created = self._create_with_csv()

        response = self.client.post(
            f"/datasets/{created['id']}/executive-summary",
            json={},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["audience"] == "equipo técnico"
        assert data["tone"] == "profesional"

    def test_executive_summary_nonexistent_returns_404(self) -> None:
        response = self.client.post(
            "/datasets/nonexistent/executive-summary",
            json={},
        )

        assert response.status_code == 404

    def test_executive_summary_bad_file_returns_422(self) -> None:
        payload = {"name": "bad", "file_path": "/missing.csv", "source_type": "csv"}
        created = self.client.post("/datasets", json=payload).json()

        response = self.client.post(
            f"/datasets/{created['id']}/executive-summary",
            json={},
        )

        assert response.status_code == 422


class _FakeRetriever(DocumentRetriever):
    def retrieve(self, query: str, top_k: int = 5) -> list[DocumentChunk]:
        return [
            DocumentChunk(source="test.md", content="Contexto de prueba", chunk_index=0),
        ]


class TestRagQueryEndpoint:

    def setup_method(self) -> None:
        self.client, self.repo = _create_test_client()
        self.client.app.dependency_overrides[get_llm_client] = lambda: _FakeLlmClient()  # type: ignore[union-attr]
        self.client.app.dependency_overrides[get_document_retriever] = lambda: _FakeRetriever()  # type: ignore[union-attr]

    def _create_with_csv(self) -> dict:
        import os

        csv_path = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__), "..", "..", "data", "sample", "test_data.csv"
            )
        )
        payload = {"name": "test", "file_path": csv_path, "source_type": "csv"}
        return self.client.post("/datasets", json=payload).json()

    def test_rag_query_returns_200(self) -> None:
        created = self._create_with_csv()

        response = self.client.post(
            f"/datasets/{created['id']}/rag-query",
            json={"question": "¿Qué datos hay?"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["dataset_id"] == created["id"]
        assert data["question"] == "¿Qué datos hay?"
        assert data["answer"] == "Resumen ejecutivo de prueba."
        assert len(data["sources"]) >= 1
        assert data["sources"][0]["source"] == "test.md"

    def test_rag_query_nonexistent_returns_404(self) -> None:
        response = self.client.post(
            "/datasets/nonexistent/rag-query",
            json={"question": "pregunta"},
        )

        assert response.status_code == 404

    def test_rag_query_bad_file_returns_422(self) -> None:
        payload = {"name": "bad", "file_path": "/missing.csv", "source_type": "csv"}
        created = self.client.post("/datasets", json=payload).json()

        response = self.client.post(
            f"/datasets/{created['id']}/rag-query",
            json={"question": "pregunta"},
        )

        assert response.status_code == 422


class TestEnrichedSummaryEndpoint:

    def setup_method(self) -> None:
        self.client, self.repo = _create_test_client()
        self.client.app.dependency_overrides[get_llm_client] = lambda: _FakeLlmClient()  # type: ignore[union-attr]
        self.client.app.dependency_overrides[get_document_retriever] = lambda: _FakeRetriever()  # type: ignore[union-attr]

    def _create_with_csv(self) -> dict:
        import os

        csv_path = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__), "..", "..", "data", "sample", "test_data.csv"
            )
        )
        payload = {"name": "test", "file_path": csv_path, "source_type": "csv"}
        return self.client.post("/datasets", json=payload).json()

    def test_enriched_summary_returns_200(self) -> None:
        created = self._create_with_csv()

        response = self.client.post(
            f"/datasets/{created['id']}/enriched-summary",
            json={"audience": "directivos", "tone": "ejecutivo"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["dataset_id"] == created["id"]
        assert data["audience"] == "directivos"

    def test_enriched_summary_nonexistent_returns_404(self) -> None:
        response = self.client.post(
            "/datasets/nonexistent/enriched-summary",
            json={},
        )

        assert response.status_code == 404
