from src.application.use_cases.list_datasets_use_case import ListDatasetsUseCase
from src.infrastructure.persistence.in_memory_dataset_repository import (
    InMemoryDatasetRepository,
)


class TestListDatasetsUseCase:

    def test_returns_empty_list_when_no_datasets(self) -> None:
        repo = InMemoryDatasetRepository()
        use_case = ListDatasetsUseCase(repository=repo)

        assert use_case.execute() == []

    def test_returns_all_saved_datasets(self) -> None:
        repo = InMemoryDatasetRepository()
        use_case = ListDatasetsUseCase(repository=repo)

        from src.domain.entities.dataset import Dataset

        repo.save(Dataset(name="a", file_path="/a.csv", source_type="csv"))
        repo.save(Dataset(name="b", file_path="/b.csv", source_type="csv"))

        result = use_case.execute()
        assert len(result) == 2
