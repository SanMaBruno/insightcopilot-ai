from __future__ import annotations

from src.application.use_cases.get_dataset_by_id_use_case import GetDatasetByIdUseCase
from src.domain.entities.chart_result import DatasetVisualization
from src.domain.repositories.chart_generator import ChartGenerator
from src.domain.repositories.dataset_repository import DatasetRepository


class GenerateDatasetVisualizationsUseCase:

    def __init__(
        self, repository: DatasetRepository, chart_generator: ChartGenerator
    ) -> None:
        self._repository = repository
        self._chart_generator = chart_generator

    def execute(self, dataset_id: str) -> DatasetVisualization:
        dataset = GetDatasetByIdUseCase(repository=self._repository).execute(dataset_id)
        charts = self._chart_generator.generate(dataset.file_path)
        return DatasetVisualization(dataset_id=dataset.id, charts=charts)
