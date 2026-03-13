from __future__ import annotations

from typing import Any

from src.shared.exceptions.ai import (
    AiServiceError,
    ApiKeyInvalidError,
    InsufficientQuotaError,
    ProviderResponseError,
    ProviderTemporaryError,
)


def _extract_error_code(exc: Exception) -> str | None:
    code = getattr(exc, "code", None)
    if isinstance(code, str) and code:
        return code

    body = getattr(exc, "body", None)
    if isinstance(body, dict):
        nested_code = body.get("code")
        if isinstance(nested_code, str) and nested_code:
            return nested_code
    return None


def map_openai_error(exc: Exception, *, service: str) -> AiServiceError:
    import openai

    if isinstance(exc, openai.AuthenticationError):
        return ApiKeyInvalidError(service=service)

    if isinstance(exc, openai.RateLimitError):
        if _extract_error_code(exc) == "insufficient_quota":
            return InsufficientQuotaError(service=service)
        return ProviderTemporaryError(service=service)

    if isinstance(
        exc,
        (
            openai.APIConnectionError,
            openai.APITimeoutError,
            openai.InternalServerError,
        ),
    ):
        return ProviderTemporaryError(service=service)

    if isinstance(exc, openai.OpenAIError):
        return ProviderResponseError(service=service)

    raise TypeError(f"Unsupported OpenAI exception: {type(exc).__name__}")
