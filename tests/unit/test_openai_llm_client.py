from __future__ import annotations

import sys
from types import SimpleNamespace

import pytest

from src.infrastructure.llm.openai_llm_client import OpenAiLlmClient
from src.shared.exceptions.ai import (
    ApiKeyInvalidError,
    InsufficientQuotaError,
    ProviderTemporaryError,
)


class _FakeOpenAIError(Exception):
    def __init__(self, code: str | None = None) -> None:
        super().__init__(code or "openai error")
        self.code = code
        self.body = {"code": code} if code else {}


class _FakeAuthenticationError(_FakeOpenAIError):
    pass


class _FakeRateLimitError(_FakeOpenAIError):
    pass


class _FakeAPIConnectionError(_FakeOpenAIError):
    pass


class _FakeAPITimeoutError(_FakeAPIConnectionError):
    pass


class _FakeInternalServerError(_FakeOpenAIError):
    pass


def _install_fake_openai(monkeypatch: pytest.MonkeyPatch, exc: Exception) -> None:
    class _FakeOpenAI:
        def __init__(self, api_key: str) -> None:
            self.api_key = api_key
            self.chat = SimpleNamespace(
                completions=SimpleNamespace(create=lambda **_: (_ for _ in ()).throw(exc))
            )

    fake_module = SimpleNamespace(
        OpenAI=_FakeOpenAI,
        OpenAIError=_FakeOpenAIError,
        AuthenticationError=_FakeAuthenticationError,
        RateLimitError=_FakeRateLimitError,
        APIConnectionError=_FakeAPIConnectionError,
        APITimeoutError=_FakeAPITimeoutError,
        InternalServerError=_FakeInternalServerError,
    )
    monkeypatch.setitem(sys.modules, "openai", fake_module)


def test_llm_maps_insufficient_quota_to_controlled_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install_fake_openai(monkeypatch, _FakeRateLimitError("insufficient_quota"))
    client = OpenAiLlmClient(api_key="test-key")

    with pytest.raises(InsufficientQuotaError) as exc_info:
        client.generate("system", "user")

    assert exc_info.value.code == "insufficient_quota"
    assert exc_info.value.category == "billing"
    assert exc_info.value.service == "llm"


def test_llm_maps_invalid_api_key_to_controlled_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install_fake_openai(monkeypatch, _FakeAuthenticationError())
    client = OpenAiLlmClient(api_key="bad-key")

    with pytest.raises(ApiKeyInvalidError):
        client.generate("system", "user")


def test_llm_maps_temporary_provider_errors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install_fake_openai(monkeypatch, _FakeAPIConnectionError())
    client = OpenAiLlmClient(api_key="test-key")

    with pytest.raises(ProviderTemporaryError) as exc_info:
        client.generate("system", "user")

    assert exc_info.value.retryable is True
