from __future__ import annotations

from src.domain.llm_client import LlmClient
from src.infrastructure.gemini_error_mapper import map_gemini_error
from src.shared.exceptions.ai import ApiKeyMissingError, ProviderClientMissingError


class GeminiLlmClient(LlmClient):
    """Cliente LLM que usa Google Gemini como proveedor cloud."""

    def __init__(self, api_key: str, model: str = "gemini-2.0-flash") -> None:
        self._api_key = api_key
        self._model = model

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        if not self._api_key:
            raise ApiKeyMissingError(service="llm")
        try:
            from google import genai
        except ImportError as exc:
            raise ProviderClientMissingError(service="llm") from exc

        client = genai.Client(api_key=self._api_key)
        try:
            response = client.models.generate_content(
                model=self._model,
                contents=user_prompt,
                config=genai.types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    temperature=0.3,
                    max_output_tokens=1024,
                ),
            )
        except Exception as exc:
            raise map_gemini_error(exc, service="llm") from exc

        return response.text or ""
