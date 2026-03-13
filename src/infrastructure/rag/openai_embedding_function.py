from __future__ import annotations

from src.infrastructure.openai_error_mapper import map_openai_error
from src.shared.exceptions.ai import ApiKeyMissingError, ProviderClientMissingError


class OpenAiEmbeddingFunction:
    """Genera embeddings usando la API de OpenAI."""

    def __init__(
        self, api_key: str, model: str = "text-embedding-3-small"
    ) -> None:
        self._api_key = api_key
        self._model = model

    def __call__(self, texts: list[str]) -> list[list[float]]:
        if not self._api_key:
            raise ApiKeyMissingError(service="embeddings")
        try:
            import openai
        except ImportError as exc:
            raise ProviderClientMissingError(service="embeddings") from exc

        client = openai.OpenAI(api_key=self._api_key)
        try:
            response = client.embeddings.create(model=self._model, input=texts)
        except openai.OpenAIError as exc:
            raise map_openai_error(exc, service="embeddings") from exc

        return [item.embedding for item in response.data]
