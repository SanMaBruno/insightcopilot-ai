import pytest

from src.application.use_cases.get_dataset_by_id_use_case import (
    DatasetNotFoundError,
    GetDatasetByIdUseCase,
)
from src.domain.entities.dataset import Dataset
from src.infrastructure.persistence.in_memory_dataset_repository import (
    InMemoryDatasetRepository,
)


class TestGetDatasetByIdUseCase:

    def test_returns_dataset_when_found(self) -> None:
        repo = InMemoryDatasetRepository()
        ds = Dataset(name="ventas", file_path="/v.csv", source_type="csv")
        repo.save(ds)

        use_case = GetDatasetByIdUseCase(repository=repo)
        result = use_case.execute(ds.id)

        assert result.id == ds.id
        assert result.name == "ventas"

    def test_raises_when_not_found(self) -> None:
        repo = InMemoryDatasetRepository()
        use_case = GetDatasetByIdUseCase(repository=repo)

        with pytest.raises(DatasetNotFoundError):
            use_case.execute("nonexistent")
