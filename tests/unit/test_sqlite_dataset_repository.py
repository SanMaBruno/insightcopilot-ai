from __future__ import annotations

import os
import tempfile

from src.domain.entities.dataset import Dataset
from src.infrastructure.persistence.sqlite_dataset_repository import (
    SqliteDatasetRepository,
)


class TestSqliteDatasetRepository:

    def setup_method(self) -> None:
        self._fd, self._db_path = tempfile.mkstemp(suffix=".db")
        os.close(self._fd)
        self.repo = SqliteDatasetRepository(db_path=self._db_path)

    def teardown_method(self) -> None:
        os.unlink(self._db_path)

    def test_save_and_get_by_id(self) -> None:
        ds = Dataset(name="ventas", file_path="/data/v.csv", source_type="csv")
        self.repo.save(ds)

        found = self.repo.get_by_id(ds.id)

        assert found is not None
        assert found.id == ds.id
        assert found.name == "ventas"
        assert found.file_path == "/data/v.csv"
        assert found.source_type == "csv"
        assert found.created_at is not None

    def test_get_by_id_returns_none_when_not_found(self) -> None:
        assert self.repo.get_by_id("nonexistent") is None

    def test_list_all_empty(self) -> None:
        assert self.repo.list_all() == []

    def test_list_all_returns_saved_datasets(self) -> None:
        ds1 = Dataset(name="a", file_path="/a.csv", source_type="csv")
        ds2 = Dataset(name="b", file_path="/b.csv", source_type="csv")
        self.repo.save(ds1)
        self.repo.save(ds2)

        result = self.repo.list_all()
        assert len(result) == 2

    def test_save_overwrites_existing(self) -> None:
        ds = Dataset(name="original", file_path="/a.csv", source_type="csv")
        self.repo.save(ds)
        ds.name = "updated"
        self.repo.save(ds)

        found = self.repo.get_by_id(ds.id)
        assert found is not None
        assert found.name == "updated"

    def test_persists_across_instances(self) -> None:
        ds = Dataset(name="persist", file_path="/p.csv", source_type="csv")
        self.repo.save(ds)

        repo2 = SqliteDatasetRepository(db_path=self._db_path)
        found = repo2.get_by_id(ds.id)

        assert found is not None
        assert found.name == "persist"
