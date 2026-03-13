from src.application.use_cases.create_dataset_use_case import CreateDatasetUseCase
from src.infrastructure.persistence.in_memory_dataset_repository import (
    InMemoryDatasetRepository,
)


class TestCreateDatasetUseCase:

    def test_creates_and_persists_dataset(self) -> None:
        repo = InMemoryDatasetRepository()
        use_case = CreateDatasetUseCase(repository=repo)

        result = use_case.execute(
            name="ventas",
            file_path="/data/ventas.csv",
            source_type="csv",
        )

        assert result.name == "ventas"
        assert result.file_path == "/data/ventas.csv"
        assert result.source_type == "csv"
        assert len(result.id) > 0

        persisted = repo.get_by_id(result.id)
        assert persisted is not None
        assert persisted.id == result.id

    def test_each_execution_creates_unique_dataset(self) -> None:
        repo = InMemoryDatasetRepository()
        use_case = CreateDatasetUseCase(repository=repo)

        ds1 = use_case.execute("a", "/a.csv", "csv")
        ds2 = use_case.execute("b", "/b.csv", "csv")

        assert ds1.id != ds2.id
        assert len(repo.list_all()) == 2
