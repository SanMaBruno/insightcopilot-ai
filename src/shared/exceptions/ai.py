from __future__ import annotations

from src.shared.exceptions.base import DomainError


def _service_label(service: str) -> str:
    if service == "embeddings":
        return "embeddings"
    return "LLM"


class AiServiceError(DomainError):
    """Error controlado para servicios de IA externos."""

    def __init__(
        self,
        message: str,
        *,
        code: str,
        category: str,
        service: str,
        status_code: int = 503,
        retryable: bool = False,
        provider: str = "openai",
    ) -> None:
        super().__init__(message)
        self.code = code
        self.category = category
        self.service = service
        self.status_code = status_code
        self.retryable = retryable
        self.provider = provider

    def to_response(self) -> dict[str, object]:
        return {
            "detail": self.message,
            "code": self.code,
            "category": self.category,
            "service": self.service,
            "provider": self.provider,
            "retryable": self.retryable,
        }


class ApiKeyMissingError(AiServiceError):
    def __init__(self, *, service: str) -> None:
        label = _service_label(service)
        super().__init__(
            f"La funcionalidad de {label} no está disponible actualmente por configuración del proveedor.",
            code="api_key_missing",
            category="configuration",
            service=service,
            status_code=503,
            retryable=False,
        )


class ProviderClientMissingError(AiServiceError):
    def __init__(self, *, service: str) -> None:
        label = _service_label(service)
        super().__init__(
            f"La funcionalidad de {label} no está disponible actualmente por configuración incompleta del backend.",
            code="provider_client_missing",
            category="configuration",
            service=service,
            status_code=503,
            retryable=False,
        )


class ApiKeyInvalidError(AiServiceError):
    def __init__(self, *, service: str) -> None:
        label = _service_label(service)
        super().__init__(
            f"La funcionalidad de {label} no está disponible actualmente por credenciales inválidas del proveedor.",
            code="api_key_invalid",
            category="authentication",
            service=service,
            status_code=503,
            retryable=False,
        )


class InsufficientQuotaError(AiServiceError):
    def __init__(self, *, service: str) -> None:
        label = _service_label(service)
        super().__init__(
            f"La funcionalidad de {label} no está disponible actualmente por cuota o billing del proveedor.",
            code="insufficient_quota",
            category="billing",
            service=service,
            status_code=503,
            retryable=False,
        )


class ProviderTemporaryError(AiServiceError):
    def __init__(self, *, service: str) -> None:
        label = _service_label(service)
        super().__init__(
            f"La funcionalidad de {label} no está disponible temporalmente por el proveedor.",
            code="provider_unavailable",
            category="temporary",
            service=service,
            status_code=503,
            retryable=True,
        )


class ProviderResponseError(AiServiceError):
    def __init__(self, *, service: str) -> None:
        label = _service_label(service)
        super().__init__(
            f"La funcionalidad de {label} no pudo completarse por un error del proveedor.",
            code="provider_error",
            category="provider",
            service=service,
            status_code=502,
            retryable=False,
        )
