from __future__ import annotations

from src.application.services.executive_summary_context_builder import (
    build_system_prompt,
)
from src.application.services.insight_generator import generate_insights
from src.application.services.rag_context_builder import build_rag_user_prompt
from src.application.use_cases.get_dataset_by_id_use_case import GetDatasetByIdUseCase
from src.application.use_cases.profile_dataset_use_case import ProfileDatasetUseCase
from src.domain.entities.executive_summary import ExecutiveSummary
from src.domain.llm_client import LlmClient
from src.domain.repositories.dataset_loader import DatasetLoader
from src.domain.repositories.dataset_repository import DatasetRepository
from src.domain.repositories.document_retriever import DocumentRetriever


class GenerateEnrichedSummaryUseCase:
    """Genera un resumen ejecutivo enriquecido con contexto documental."""

    def __init__(
        self,
        repository: DatasetRepository,
        loader: DatasetLoader,
        retriever: DocumentRetriever,
        llm_client: LlmClient,
    ) -> None:
        self._repository = repository
        self._loader = loader
        self._retriever = retriever
        self._llm_client = llm_client

    def execute(
        self,
        dataset_id: str,
        audience: str = "equipo técnico",
        tone: str = "profesional",
        max_paragraphs: int = 3,
        top_k: int = 5,
    ) -> ExecutiveSummary:
        dataset = GetDatasetByIdUseCase(repository=self._repository).execute(dataset_id)

        profile = ProfileDatasetUseCase(
            repository=self._repository, loader=self._loader
        ).execute(dataset_id)

        report = generate_insights(profile)

        chunks = self._retriever.retrieve(
            f"resumen ejecutivo {dataset.name}", top_k=top_k
        )

        system_prompt = build_system_prompt(audience, tone, max_paragraphs)
        user_prompt = build_rag_user_prompt(
            dataset.name, profile, report, chunks,
            "Genera un resumen ejecutivo basado exclusivamente en esta información.",
        )

        content = self._llm_client.generate(system_prompt, user_prompt)

        return ExecutiveSummary(
            dataset_id=dataset_id,
            audience=audience,
            tone=tone,
            content=content,
        )
