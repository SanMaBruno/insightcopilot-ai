from src.application.services.insight_generator import generate_insights
from src.application.use_cases.profile_dataset_use_case import ProfileDatasetUseCase
from src.domain.entities.dataset_insight import DatasetInsightReport
from src.domain.repositories.dataset_loader import DatasetLoader
from src.domain.repositories.dataset_repository import DatasetRepository


class GenerateDatasetInsightsUseCase:

    def __init__(
        self,
        repository: DatasetRepository,
        loader: DatasetLoader,
    ) -> None:
        self._repository = repository
        self._loader = loader

    def execute(self, dataset_id: str) -> DatasetInsightReport:
        profile = ProfileDatasetUseCase(
            repository=self._repository, loader=self._loader
        ).execute(dataset_id)
        return generate_insights(profile)
