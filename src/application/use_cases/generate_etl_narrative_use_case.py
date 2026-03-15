from __future__ import annotations

import re

from src.application.services.etl_narrative_context_builder import (
    build_system_prompt,
    build_user_prompt,
)
from src.domain.entities.etl_narrative import EtlNarrative
from src.domain.llm_client import LlmClient
from src.domain.repositories.curated_result_repository import CuratedResultRepository
from src.domain.value_objects.etl_narrative_sections import EtlNarrativeSections


class CuratedResultNotFoundError(Exception):
    def __init__(self, dataset_id: str, etl_run_id: str) -> None:
        self.message = (
            f"No se encontró resultado curado para dataset '{dataset_id}' "
            f"y etl_run_id '{etl_run_id}'"
        )
        super().__init__(self.message)


_SECTION_PATTERN = re.compile(
    r"## (RESUMEN|CALIDAD_ORIGINAL|TRANSFORMACIONES|RESULTADO|RECOMENDACIONES)\s*\n",
)

_DEFAULT_TEXT = "Información no disponible."


def _parse_sections(raw: str) -> EtlNarrativeSections:
    parts: dict[str, str] = {}
    splits = _SECTION_PATTERN.split(raw)

    # splits alternates: [preamble, header1, body1, header2, body2, ...]
    for i in range(1, len(splits) - 1, 2):
        key = splits[i].strip().lower()
        body = splits[i + 1].strip()
        parts[key] = body

    return EtlNarrativeSections(
        resumen=parts.get("resumen", _DEFAULT_TEXT),
        calidad_original=parts.get("calidad_original", _DEFAULT_TEXT),
        transformaciones=parts.get("transformaciones", _DEFAULT_TEXT),
        resultado=parts.get("resultado", _DEFAULT_TEXT),
        recomendaciones=parts.get("recomendaciones", _DEFAULT_TEXT),
    )


class GenerateEtlNarrativeUseCase:

    def __init__(
        self,
        curated_repo: CuratedResultRepository,
        llm_client: LlmClient,
    ) -> None:
        self._curated_repo = curated_repo
        self._llm_client = llm_client

    def execute(self, dataset_id: str, etl_run_id: str) -> EtlNarrative:
        result = self._curated_repo.get_by_run(dataset_id, etl_run_id)
        if result is None:
            raise CuratedResultNotFoundError(dataset_id, etl_run_id)

        system_prompt = build_system_prompt()
        user_prompt = build_user_prompt(result)

        raw_response = self._llm_client.generate(system_prompt, user_prompt)
        sections = _parse_sections(raw_response)

        return EtlNarrative(
            dataset_id=dataset_id,
            etl_run_id=etl_run_id,
            sections=sections,
            execution_mode=result.execution_mode,
        )
