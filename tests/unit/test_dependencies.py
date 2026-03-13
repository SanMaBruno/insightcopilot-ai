from __future__ import annotations

from src.infrastructure.llm.mock_llm_client import MockLlmClient
from src.presentation.api.dependencies import build_llm_client, build_vector_store
from src.shared.config.settings import Settings


def test_build_llm_client_returns_mock_in_mock_mode() -> None:
    config = Settings(app_env="test", llm_mode="mock")

    client = build_llm_client(config)

    assert isinstance(client, MockLlmClient)


def test_build_vector_store_uses_mock_embeddings_in_mock_mode() -> None:
    config = Settings(app_env="test", llm_mode="mock")
    store = build_vector_store(config)

    indexed = store.index("demo.txt", ["ventas trimestrales", "ciudades principales"])
    results = store.retrieve("ventas", top_k=1)

    assert indexed == 2
    assert len(results) == 1
    assert results[0].source == "demo.txt"
