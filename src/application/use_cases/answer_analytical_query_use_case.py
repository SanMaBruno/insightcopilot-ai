from __future__ import annotations

from src.application.services.insight_generator import generate_insights
from src.application.services.query_resolver import build_answer, detect_intent
from src.application.use_cases.profile_dataset_use_case import ProfileDatasetUseCase
from src.domain.entities.analytical_query import AnalyticalAnswer
from src.domain.repositories.dataset_loader import DatasetLoader
from src.domain.repositories.dataset_repository import DatasetRepository


class AnswerAnalyticalQueryUseCase:

    def __init__(
        self, repository: DatasetRepository, loader: DatasetLoader
    ) -> None:
        self._repository = repository
        self._loader = loader

    def execute(self, dataset_id: str, question: str) -> AnalyticalAnswer:
        profile = ProfileDatasetUseCase(
            repository=self._repository, loader=self._loader
        ).execute(dataset_id)
        report = generate_insights(profile)
        intent = detect_intent(question)
        return build_answer(question, intent, profile, report)
