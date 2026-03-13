from __future__ import annotations

from fastapi.testclient import TestClient

from src.presentation.api.app import create_app
from src.shared.exceptions.base import DomainError


def _create_test_client() -> TestClient:
    app = create_app()
    return TestClient(app)


class TestHealthEndpoint:
    def test_health_returns_ok(self) -> None:
        client = _create_test_client()
        response = client.get("/health")
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "ok"
        assert "version" in body

    def test_health_response_schema(self) -> None:
        client = _create_test_client()
        response = client.get("/health")
        body = response.json()
        assert set(body.keys()) == {"status", "version"}


class TestCorsHeaders:
    def test_cors_allows_any_origin(self) -> None:
        client = _create_test_client()
        response = client.options(
            "/health",
            headers={
                "Origin": "http://example.com",
                "Access-Control-Request-Method": "GET",
            },
        )
        assert response.headers.get("access-control-allow-origin") == "*"


class TestGlobalErrorHandlers:
    def test_domain_error_returns_400(self) -> None:
        app = create_app()

        @app.get("/test-domain-error")
        def _raise_domain_error() -> None:
            raise DomainError("campo inválido")

        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/test-domain-error")
        assert response.status_code == 400
        assert response.json()["detail"] == "campo inválido"

    def test_unhandled_error_returns_500(self) -> None:
        app = create_app()

        @app.get("/test-unhandled-error")
        def _raise_unexpected() -> None:
            raise RuntimeError("boom")

        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/test-unhandled-error")
        assert response.status_code == 500
        assert response.json()["detail"] == "Error interno del servidor."
