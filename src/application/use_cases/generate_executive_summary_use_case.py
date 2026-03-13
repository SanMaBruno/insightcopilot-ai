from __future__ import annotations

from src.application.services.executive_summary_context_builder import (
    build_system_prompt,
    build_user_prompt,
)
from src.application.services.insight_generator import generate_insights
from src.application.use_cases.get_dataset_by_id_use_case import GetDatasetByIdUseCase
from src.application.use_cases.profile_dataset_use_case import ProfileDatasetUseCase
from src.domain.entities.executive_summary import ExecutiveSummary
from src.domain.llm_client import LlmClient
from src.domain.repositories.dataset_loader import DatasetLoader
from src.domain.repositories.dataset_repository import DatasetRepository


class GenerateExecutiveSummaryUseCase:

    def __init__(
        self,
        repository: DatasetRepository,
        loader: DatasetLoader,
        llm_client: LlmClient,
    ) -> None:
        self._repository = repository
        self._loader = loader
        self._llm_client = llm_client

    def execute(
        self,
        dataset_id: str,
        audience: str = "equipo técnico",
        tone: str = "profesional",
        max_paragraphs: int = 3,
    ) -> ExecutiveSummary:
        dataset = GetDatasetByIdUseCase(repository=self._repository).execute(dataset_id)

        profile = ProfileDatasetUseCase(
            repository=self._repository, loader=self._loader
        ).execute(dataset_id)

        report = generate_insights(profile)

        system_prompt = build_system_prompt(audience, tone, max_paragraphs)
        user_prompt = build_user_prompt(dataset.name, profile, report)

        content = self._llm_client.generate(system_prompt, user_prompt)

        return ExecutiveSummary(
            dataset_id=dataset_id,
            audience=audience,
            tone=tone,
            content=content,
        )
