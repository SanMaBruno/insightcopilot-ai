from __future__ import annotations

import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread

import pytest

from src.infrastructure.llm.ollama_llm_client import OllamaLlmClient
from src.shared.exceptions.ai import ProviderTemporaryError


class _FakeOllamaHandler(BaseHTTPRequestHandler):
    """Handler HTTP simple que simula el endpoint /api/chat de Ollama."""

    response_body: str = ""

    def do_POST(self) -> None:  # noqa: N802
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length))
        _FakeOllamaHandler.last_request = body

        reply = {
            "message": {"role": "assistant", "content": self.response_body},
        }
        data = json.dumps(reply).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, format: str, *args: object) -> None:  # noqa: A002
        pass  # silenciar logs del test server


class TestOllamaLlmClient:

    def test_returns_content_from_ollama_response(self) -> None:
        server = HTTPServer(("127.0.0.1", 0), _FakeOllamaHandler)
        port = server.server_address[1]
        _FakeOllamaHandler.response_body = "Respuesta de Ollama."

        thread = Thread(target=server.handle_request, daemon=True)
        thread.start()

        client = OllamaLlmClient(
            base_url=f"http://127.0.0.1:{port}", model="test-model",
        )
        result = client.generate("system prompt", "user prompt")

        assert result == "Respuesta de Ollama."

        thread.join(timeout=2)
        server.server_close()

    def test_sends_correct_payload(self) -> None:
        server = HTTPServer(("127.0.0.1", 0), _FakeOllamaHandler)
        port = server.server_address[1]
        _FakeOllamaHandler.response_body = "ok"

        thread = Thread(target=server.handle_request, daemon=True)
        thread.start()

        client = OllamaLlmClient(
            base_url=f"http://127.0.0.1:{port}", model="llama3.2",
        )
        client.generate("sys", "usr")

        req = _FakeOllamaHandler.last_request
        assert req["model"] == "llama3.2"
        assert req["stream"] is False
        assert req["messages"][0]["role"] == "system"
        assert req["messages"][0]["content"] == "sys"
        assert req["messages"][1]["role"] == "user"
        assert req["messages"][1]["content"] == "usr"

        thread.join(timeout=2)
        server.server_close()

    def test_raises_temporary_error_on_connection_failure(self) -> None:
        client = OllamaLlmClient(
            base_url="http://127.0.0.1:1", model="test",
        )

        with pytest.raises(ProviderTemporaryError):
            client.generate("system", "user")

    def test_stores_config(self) -> None:
        client = OllamaLlmClient(
            base_url="http://myhost:11434", model="mistral",
        )

        assert client._base_url == "http://myhost:11434"
        assert client._model == "mistral"

    def test_docstring_documents_ollama_limitations(self) -> None:
        assert "RAG" in OllamaLlmClient.__doc__
        assert "embedding" in OllamaLlmClient.__doc__.lower()
