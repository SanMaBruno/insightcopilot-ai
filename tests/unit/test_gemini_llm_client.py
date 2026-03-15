from __future__ import annotations

import pytest

from src.shared.exceptions.ai import ApiKeyMissingError


class TestGeminiLlmClient:

    def test_raises_when_api_key_missing(self) -> None:
        from src.infrastructure.llm.gemini_llm_client import GeminiLlmClient

        client = GeminiLlmClient(api_key="", model="gemini-2.0-flash")

        with pytest.raises(ApiKeyMissingError):
            client.generate("system", "user")

    def test_raises_when_sdk_not_installed(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from src.infrastructure.llm.gemini_llm_client import GeminiLlmClient

        client = GeminiLlmClient(api_key="fake-key", model="gemini-2.0-flash")

        import builtins

        real_import = builtins.__import__

        def _block_google(name: str, *args, **kwargs):  # type: ignore[no-untyped-def]
            if name == "google" or name.startswith("google."):
                raise ImportError("mocked")
            return real_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", _block_google)

        from src.shared.exceptions.ai import ProviderClientMissingError

        with pytest.raises(ProviderClientMissingError):
            client.generate("system", "user")

    def test_stores_api_key_and_model(self) -> None:
        from src.infrastructure.llm.gemini_llm_client import GeminiLlmClient

        client = GeminiLlmClient(api_key="test-key", model="gemini-pro")

        assert client._api_key == "test-key"
        assert client._model == "gemini-pro"


class TestGeminiErrorMapper:

    def test_maps_generic_exception_to_provider_response_error(self) -> None:
        from src.infrastructure.gemini_error_mapper import map_gemini_error
        from src.shared.exceptions.ai import ProviderResponseError

        err = map_gemini_error(RuntimeError("unexpected"), service="llm")

        assert isinstance(err, ProviderResponseError)


class TestGeminiEmbeddingFunction:

    def test_raises_when_api_key_missing(self) -> None:
        from src.infrastructure.rag.gemini_embedding_function import GeminiEmbeddingFunction

        fn = GeminiEmbeddingFunction(api_key="", model="text-embedding-004")

        with pytest.raises(ApiKeyMissingError):
            fn(["hello"])

    def test_raises_when_sdk_not_installed(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from src.infrastructure.rag.gemini_embedding_function import GeminiEmbeddingFunction

        fn = GeminiEmbeddingFunction(api_key="fake-key", model="text-embedding-004")

        import builtins

        real_import = builtins.__import__

        def _block_google(name: str, *args, **kwargs):  # type: ignore[no-untyped-def]
            if name == "google" or name.startswith("google."):
                raise ImportError("mocked")
            return real_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", _block_google)

        from src.shared.exceptions.ai import ProviderClientMissingError

        with pytest.raises(ProviderClientMissingError):
            fn(["hello"])
