from src.domain.entities.dataset import Dataset
from src.infrastructure.persistence.in_memory_dataset_repository import (
    InMemoryDatasetRepository,
)


class TestInMemoryDatasetRepository:

    def _make_dataset(self, name: str = "ventas") -> Dataset:
        return Dataset(name=name, file_path="/data/ventas.csv", source_type="csv")

    def test_save_and_get_by_id(self) -> None:
        repo = InMemoryDatasetRepository()
        ds = self._make_dataset()

        repo.save(ds)
        result = repo.get_by_id(ds.id)

        assert result is not None
        assert result.id == ds.id
        assert result.name == "ventas"

    def test_get_by_id_returns_none_when_not_found(self) -> None:
        repo = InMemoryDatasetRepository()

        assert repo.get_by_id("nonexistent") is None

    def test_list_all_empty(self) -> None:
        repo = InMemoryDatasetRepository()

        assert repo.list_all() == []

    def test_list_all_returns_saved_datasets(self) -> None:
        repo = InMemoryDatasetRepository()
        ds1 = self._make_dataset("ventas")
        ds2 = self._make_dataset("clientes")

        repo.save(ds1)
        repo.save(ds2)

        result = repo.list_all()
        assert len(result) == 2

    def test_save_overwrites_existing(self) -> None:
        repo = InMemoryDatasetRepository()
        ds = self._make_dataset()
        repo.save(ds)

        ds.name = "ventas_v2"
        repo.save(ds)

        result = repo.get_by_id(ds.id)
        assert result is not None
        assert result.name == "ventas_v2"
        assert len(repo.list_all()) == 1
