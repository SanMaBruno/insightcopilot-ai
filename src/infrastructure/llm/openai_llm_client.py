from __future__ import annotations

from src.domain.llm_client import LlmClient
from src.infrastructure.openai_error_mapper import map_openai_error
from src.shared.exceptions.ai import ApiKeyMissingError, ProviderClientMissingError


class OpenAiLlmClient(LlmClient):

    def __init__(self, api_key: str, model: str = "gpt-4o-mini") -> None:
        self._api_key = api_key
        self._model = model

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        if not self._api_key:
            raise ApiKeyMissingError(service="llm")
        try:
            import openai
        except ImportError as exc:
            raise ProviderClientMissingError(service="llm") from exc
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
        except openai.OpenAIError as exc:
            raise map_openai_error(exc, service="llm") from exc

        choice = response.choices[0]
        return choice.message.content or ""
