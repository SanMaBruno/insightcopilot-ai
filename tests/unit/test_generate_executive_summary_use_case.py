from __future__ import annotations

import os

from src.application.use_cases.generate_executive_summary_use_case import (
    GenerateExecutiveSummaryUseCase,
)
from src.domain.llm_client import LlmClient
from src.infrastructure.files.csv_dataset_loader import CsvDatasetLoader
from src.infrastructure.persistence.in_memory_dataset_repository import (
    InMemoryDatasetRepository,
)


class _FakeLlmClient(LlmClient):
    """LLM stub que devuelve texto fijo sin hacer llamadas reales."""

    def __init__(self, response: str = "Resumen generado por fake LLM.") -> None:
        self._response = response
        self.last_system_prompt: str | None = None
        self.last_user_prompt: str | None = None

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        self.last_system_prompt = system_prompt
        self.last_user_prompt = user_prompt
        return self._response


_CSV_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "data", "sample", "test_data.csv")
)


class TestGenerateExecutiveSummaryUseCase:

    def setup_method(self) -> None:
        self.repo = InMemoryDatasetRepository()
        self.loader = CsvDatasetLoader()
        self.llm = _FakeLlmClient()
        self.use_case = GenerateExecutiveSummaryUseCase(
            repository=self.repo, loader=self.loader, llm_client=self.llm,
        )

    def _create_dataset(self) -> str:
        from src.application.use_cases.create_dataset_use_case import CreateDatasetUseCase

        ds = CreateDatasetUseCase(repository=self.repo).execute(
            name="test", file_path=_CSV_PATH, source_type="csv",
        )
        return ds.id

    def test_returns_executive_summary(self) -> None:
        ds_id = self._create_dataset()

        result = self.use_case.execute(ds_id)

        assert result.dataset_id == ds_id
        assert result.content == "Resumen generado por fake LLM."
        assert result.audience == "equipo técnico"
        assert result.tone == "profesional"

    def test_passes_audience_and_tone(self) -> None:
        ds_id = self._create_dataset()

        result = self.use_case.execute(
            ds_id, audience="directivos", tone="ejecutivo", max_paragraphs=5,
        )

        assert result.audience == "directivos"
        assert result.tone == "ejecutivo"

    def test_system_prompt_contains_guardrails(self) -> None:
        ds_id = self._create_dataset()

        self.use_case.execute(ds_id)

        assert self.llm.last_system_prompt is not None
        assert "ÚNICAMENTE" in self.llm.last_system_prompt

    def test_user_prompt_contains_dataset_context(self) -> None:
        ds_id = self._create_dataset()

        self.use_case.execute(ds_id)

        assert self.llm.last_user_prompt is not None
        assert "test" in self.llm.last_user_prompt
        assert "3" in self.llm.last_user_prompt  # row_count from test_data.csv

    def test_raises_when_dataset_not_found(self) -> None:
        import pytest

        from src.application.use_cases.get_dataset_by_id_use_case import DatasetNotFoundError

        with pytest.raises(DatasetNotFoundError):
            self.use_case.execute("nonexistent")

    def test_custom_llm_response(self) -> None:
        custom_llm = _FakeLlmClient(response="Resumen personalizado.")
        use_case = GenerateExecutiveSummaryUseCase(
            repository=self.repo, loader=self.loader, llm_client=custom_llm,
        )
        ds_id = self._create_dataset()

        result = use_case.execute(ds_id)

        assert result.content == "Resumen personalizado."
