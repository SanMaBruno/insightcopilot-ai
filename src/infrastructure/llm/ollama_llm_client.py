from __future__ import annotations

import json
from urllib.error import URLError
from urllib.request import Request, urlopen

from src.domain.llm_client import LlmClient
from src.shared.exceptions.ai import ProviderResponseError, ProviderTemporaryError


class OllamaLlmClient(LlmClient):
    """Cliente LLM que usa Ollama local vía HTTP.

    Limitaciones conocidas en esta fase:
    - Soporta generación de texto (summary, narrativa ETL).
    - RAG con recuperación semántica real requiere un embedding_mode
      distinto de 'local' (por ejemplo 'gemini') ya que Ollama no
      expone un endpoint de embeddings compatible con el protocolo actual.
    """

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "llama3.2",
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._model = model

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        payload = json.dumps({
            "model": self._model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "stream": False,
            "options": {"temperature": 0.3},
        }).encode("utf-8")

        req = Request(
            f"{self._base_url}/api/chat",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urlopen(req, timeout=120) as resp:  # noqa: S310
                body = json.loads(resp.read().decode("utf-8"))
        except URLError as exc:
            raise ProviderTemporaryError(service="llm") from exc
        except (json.JSONDecodeError, ValueError) as exc:
            raise ProviderResponseError(service="llm") from exc

        message = body.get("message", {})
        return message.get("content", "")
