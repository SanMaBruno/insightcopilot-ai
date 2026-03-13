from __future__ import annotations

from src.shared.exceptions.base import DomainError


class EmbeddingConfigurationError(DomainError):
    pass


class EmbeddingGenerationError(DomainError):
    pass


class OpenAiEmbeddingFunction:
    """Genera embeddings usando la API de OpenAI."""

    def __init__(
        self, api_key: str, model: str = "text-embedding-3-small"
    ) -> None:
        self._api_key = api_key
        self._model = model

    def __call__(self, texts: list[str]) -> list[list[float]]:
        if not self._api_key:
            raise EmbeddingConfigurationError(
                "OPENAI_API_KEY no está configurada para embeddings."
            )
        try:
            import openai
        except ImportError as exc:
            raise EmbeddingConfigurationError(
                "El paquete 'openai' no está instalado. Ejecuta: pip install openai"
            ) from exc

        client = openai.OpenAI(api_key=self._api_key)
        try:
            response = client.embeddings.create(model=self._model, input=texts)
        except openai.AuthenticationError as exc:
            raise EmbeddingConfigurationError(
                "API key de OpenAI inválida para embeddings."
            ) from exc
        except openai.OpenAIError as exc:
            raise EmbeddingGenerationError(
                f"Error al generar embeddings: {exc}"
            ) from exc

        return [item.embedding for item in response.data]
