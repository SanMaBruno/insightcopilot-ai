from datetime import datetime

from src.domain.entities.dataset import Dataset


class TestDataset:

    def test_create_with_defaults(self) -> None:
        ds = Dataset(name="ventas", file_path="/data/ventas.csv", source_type="csv")

        assert ds.name == "ventas"
        assert ds.file_path == "/data/ventas.csv"
        assert ds.source_type == "csv"
        assert isinstance(ds.id, str)
        assert len(ds.id) > 0
        assert isinstance(ds.created_at, datetime)

    def test_create_with_explicit_id(self) -> None:
        ds = Dataset(
            name="clientes",
            file_path="/data/clientes.csv",
            source_type="csv",
            id="custom-123",
        )

        assert ds.id == "custom-123"

    def test_two_datasets_have_different_ids(self) -> None:
        ds1 = Dataset(name="a", file_path="/a.csv", source_type="csv")
        ds2 = Dataset(name="b", file_path="/b.csv", source_type="csv")

        assert ds1.id != ds2.id
