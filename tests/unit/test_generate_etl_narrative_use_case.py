from __future__ import annotations

from typing import Optional

import pytest

from src.application.use_cases.generate_etl_narrative_use_case import (
    CuratedResultNotFoundError,
    GenerateEtlNarrativeUseCase,
    _parse_sections,
)
from src.domain.entities.curated_result import CuratedResult
from src.domain.llm_client import LlmClient
from src.domain.repositories.curated_result_repository import CuratedResultRepository
from src.domain.value_objects.executed_step import ExecutedStep
from src.domain.value_objects.transformation_step import TransformAction


# ---- Fakes ----

_MOCK_LLM_RESPONSE = (
    "## RESUMEN\nResumen de prueba.\n\n"
    "## CALIDAD_ORIGINAL\nCalidad de prueba.\n\n"
    "## TRANSFORMACIONES\nTransformaciones de prueba.\n\n"
    "## RESULTADO\nResultado de prueba.\n\n"
    "## RECOMENDACIONES\nRecomendaciones de prueba."
)


class _FakeLlmClient(LlmClient):
    def __init__(self, response: str = _MOCK_LLM_RESPONSE) -> None:
        self._response = response
        self.last_system_prompt: Optional[str] = None
        self.last_user_prompt: Optional[str] = None

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        self.last_system_prompt = system_prompt
        self.last_user_prompt = user_prompt
        return self._response


class _FakeCuratedResultRepository(CuratedResultRepository):
    def __init__(self) -> None:
        self._store: dict[str, CuratedResult] = {}

    def save(self, result: CuratedResult) -> None:
        key = f"{result.dataset_id}:{result.etl_run_id}"
        self._store[key] = result

    def get_by_run(self, dataset_id: str, etl_run_id: str) -> Optional[CuratedResult]:
        return self._store.get(f"{dataset_id}:{etl_run_id}")

    def get_latest_by_dataset(self, dataset_id: str) -> Optional[CuratedResult]:
        for result in reversed(list(self._store.values())):
            if result.dataset_id == dataset_id:
                return result
        return None


def _make_result(**overrides) -> CuratedResult:
    defaults = dict(
        dataset_id="ds-1",
        etl_run_id="run-1",
        plan_id="plan-1",
        strategy="conservative",
        status="completed",
        curated_file_path="/tmp/curated.csv",
        original_row_count=100,
        curated_row_count=95,
        original_column_count=10,
        curated_column_count=8,
        original_null_count=20,
        curated_null_count=0,
        executed_steps=[
            ExecutedStep(
                action=TransformAction.FILL_NULLS_MEDIAN,
                column_name="age",
                success=True,
                rows_before=100,
                rows_after=100,
                columns_before=10,
                columns_after=10,
                detail="Mediana aplicada",
            ),
        ],
        execution_time_ms=42,
        execution_mode="manual",
    )
    defaults.update(overrides)
    return CuratedResult(**defaults)


# ---- Tests ----


class TestParseSections:

    def test_parses_all_sections(self) -> None:
        sections = _parse_sections(_MOCK_LLM_RESPONSE)
        assert sections.resumen == "Resumen de prueba."
        assert sections.calidad_original == "Calidad de prueba."
        assert sections.transformaciones == "Transformaciones de prueba."
        assert sections.resultado == "Resultado de prueba."
        assert sections.recomendaciones == "Recomendaciones de prueba."

    def test_missing_sections_get_default(self) -> None:
        raw = "## RESUMEN\nSolo resumen."
        sections = _parse_sections(raw)
        assert sections.resumen == "Solo resumen."
        assert sections.calidad_original == "Información no disponible."


class TestGenerateEtlNarrativeUseCase:

    def setup_method(self) -> None:
        self.repo = _FakeCuratedResultRepository()
        self.llm = _FakeLlmClient()
        self.use_case = GenerateEtlNarrativeUseCase(
            curated_repo=self.repo,
            llm_client=self.llm,
        )

    def test_returns_narrative_with_parsed_sections(self) -> None:
        result = _make_result()
        self.repo.save(result)

        narrative = self.use_case.execute("ds-1", "run-1")

        assert narrative.dataset_id == "ds-1"
        assert narrative.etl_run_id == "run-1"
        assert narrative.sections.resumen == "Resumen de prueba."
        assert narrative.sections.recomendaciones == "Recomendaciones de prueba."
        assert narrative.execution_mode == "manual"

    def test_raises_when_curated_result_not_found(self) -> None:
        with pytest.raises(CuratedResultNotFoundError):
            self.use_case.execute("ds-1", "nonexistent")

    def test_system_prompt_contains_guardrails(self) -> None:
        result = _make_result()
        self.repo.save(result)

        self.use_case.execute("ds-1", "run-1")

        assert self.llm.last_system_prompt is not None
        assert "ÚNICAMENTE" in self.llm.last_system_prompt
        assert "NUNCA decidir" in self.llm.last_system_prompt

    def test_user_prompt_contains_etl_context(self) -> None:
        result = _make_result()
        self.repo.save(result)

        self.use_case.execute("ds-1", "run-1")

        assert self.llm.last_user_prompt is not None
        assert "== ETL CONTEXT ==" in self.llm.last_user_prompt
        assert "100" in self.llm.last_user_prompt
        assert "conservative" in self.llm.last_user_prompt

    def test_propagates_execution_mode(self) -> None:
        result = _make_result(execution_mode="auto_safe")
        self.repo.save(result)

        narrative = self.use_case.execute("ds-1", "run-1")

        assert narrative.execution_mode == "auto_safe"

    def test_narrative_has_id_and_created_at(self) -> None:
        result = _make_result()
        self.repo.save(result)

        narrative = self.use_case.execute("ds-1", "run-1")

        assert narrative.id is not None
        assert len(narrative.id) > 0
        assert narrative.created_at is not None
