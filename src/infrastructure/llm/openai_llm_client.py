from __future__ import annotations

from src.domain.llm_client import LlmClient
from src.shared.exceptions.base import DomainError


class LlmConfigurationError(DomainError):
    pass


class LlmGenerationError(DomainError):
    pass


class OpenAiLlmClient(LlmClient):

    def __init__(self, api_key: str, model: str = "gpt-4o-mini") -> None:
        self._api_key = api_key
        self._model = model

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        if not self._api_key:
            raise LlmConfigurationError(
                "OPENAI_API_KEY no está configurada. "
                "Agregala al archivo .env para usar resúmenes ejecutivos."
            )
        try:
            import openai
        except ImportError as exc:
            raise LlmConfigurationError(
                "El paquete 'openai' no está instalado. Ejecuta: pip install openai"
            ) from exc

        client = openai.OpenAI(api_key=self._api_key)
        try:
            response = client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=1024,
                temperature=0.3,
            )
        except openai.AuthenticationError as exc:
            raise LlmConfigurationError(
                "API key de OpenAI inválida."
            ) from exc
        except openai.OpenAIError as exc:
            raise LlmGenerationError(
                f"Error al generar resumen con OpenAI: {exc}"
            ) from exc

        choice = response.choices[0]
        return choice.message.content or ""
