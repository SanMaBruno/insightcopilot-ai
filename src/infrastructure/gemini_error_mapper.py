from __future__ import annotations

from src.shared.exceptions.ai import (
    AiServiceError,
    ApiKeyInvalidError,
    InsufficientQuotaError,
    ProviderResponseError,
    ProviderTemporaryError,
)


def map_gemini_error(exc: Exception, *, service: str) -> AiServiceError:
    from google.genai import errors as genai_errors

    exc_type = type(exc).__name__
    message = str(exc).lower()

    if isinstance(exc, genai_errors.ClientError):
        if "api_key" in message or "authenticate" in message or "permission" in message:
            return ApiKeyInvalidError(service=service)
        if "quota" in message or "resource_exhausted" in message:
            return InsufficientQuotaError(service=service)
        return ProviderResponseError(service=service)

    if isinstance(exc, genai_errors.ServerError):
        return ProviderTemporaryError(service=service)

    return ProviderResponseError(service=service)
