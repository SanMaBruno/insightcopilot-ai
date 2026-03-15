from __future__ import annotations

from src.infrastructure.gemini_error_mapper import map_gemini_error
from src.shared.exceptions.ai import ApiKeyMissingError, ProviderClientMissingError


class GeminiEmbeddingFunction:
    """Genera embeddings usando la API de Google Gemini."""

    def __init__(
        self, api_key: str, model: str = "text-embedding-004",
    ) -> None:
        self._api_key = api_key
        self._model = model

    def __call__(self, texts: list[str]) -> list[list[float]]:
        if not self._api_key:
            raise ApiKeyMissingError(service="embeddings")
        try:
            from google import genai
        except ImportError as exc:
            raise ProviderClientMissingError(service="embeddings") from exc

        client = genai.Client(api_key=self._api_key)
        try:
            response = client.models.embed_content(
                model=self._model,
                contents=texts,
            )
        except Exception as exc:
            raise map_gemini_error(exc, service="embeddings") from exc

        return [e.values for e in response.embeddings]
