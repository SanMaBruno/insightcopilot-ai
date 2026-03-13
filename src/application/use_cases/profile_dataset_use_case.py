from src.application.use_cases.get_dataset_by_id_use_case import GetDatasetByIdUseCase
from src.domain.entities.dataset_profile import DatasetProfile
from src.domain.repositories.dataset_loader import DatasetLoader
from src.domain.repositories.dataset_repository import DatasetRepository
from src.domain.value_objects.column_profile import ColumnProfile


class ProfileDatasetUseCase:

    def __init__(
        self,
        repository: DatasetRepository,
        loader: DatasetLoader,
    ) -> None:
        self._repository = repository
        self._loader = loader

    def execute(self, dataset_id: str) -> DatasetProfile:
        dataset = GetDatasetByIdUseCase(self._repository).execute(dataset_id)
        raw = self._loader.load(dataset.file_path)

        columns = [
            ColumnProfile(
                name=col,
                dtype=raw.dtypes[col],
                null_count=raw.null_counts[col],
                unique_count=raw.unique_counts[col],
            )
            for col in raw.columns
        ]

        return DatasetProfile(
            dataset_id=dataset.id,
            row_count=raw.row_count,
            column_count=len(raw.columns),
            columns=columns,
        )
