from __future__ import annotations

from src.application.use_cases.upload_dataset_use_case import UploadDatasetUseCase
from src.domain.repositories.file_storage import FileStorage
from src.infrastructure.persistence.in_memory_dataset_repository import (
    InMemoryDatasetRepository,
)


class _FakeFileStorage(FileStorage):

    def __init__(self) -> None:
        self.saved: list[tuple[str, bytes]] = []

    def save(self, filename: str, content: bytes) -> str:
        self.saved.append((filename, content))
        return f"/uploads/{filename}"


class TestUploadDatasetUseCase:

    def setup_method(self) -> None:
        self.repo = InMemoryDatasetRepository()
        self.storage = _FakeFileStorage()
        self.use_case = UploadDatasetUseCase(
            repository=self.repo, file_storage=self.storage
        )

    def test_uploads_and_persists_dataset(self) -> None:
        ds = self.use_case.execute(
            name="ventas", filename="ventas.csv", content=b"a,b\n1,2"
        )

        assert ds.name == "ventas"
        assert ds.file_path == "/uploads/ventas.csv"
        assert ds.source_type == "csv"
        assert self.repo.get_by_id(ds.id) is not None
        assert len(self.storage.saved) == 1

    def test_each_upload_creates_unique_dataset(self) -> None:
        ds1 = self.use_case.execute("a", "a.csv", b"data")
        ds2 = self.use_case.execute("b", "b.csv", b"data")

        assert ds1.id != ds2.id
        assert len(self.repo.list_all()) == 2
