from __future__ import annotations

import os
import tempfile

from src.infrastructure.files.local_file_storage import LocalFileStorage


class TestLocalFileStorage:

    def setup_method(self) -> None:
        self._tmp_dir = tempfile.mkdtemp()
        self.storage = LocalFileStorage(base_dir=self._tmp_dir)

    def test_saves_file_and_returns_absolute_path(self) -> None:
        path = self.storage.save("test.csv", b"a,b\n1,2")

        assert os.path.isabs(path)
        assert os.path.isfile(path)
        with open(path, "rb") as f:
            assert f.read() == b"a,b\n1,2"

    def test_filename_is_sanitized(self) -> None:
        path = self.storage.save("../../etc/passwd", b"data")

        basename = os.path.basename(path)
        assert "/" not in basename
        assert ".." not in basename

    def test_two_saves_produce_different_paths(self) -> None:
        p1 = self.storage.save("test.csv", b"a")
        p2 = self.storage.save("test.csv", b"b")

        assert p1 != p2

    def test_creates_directory_if_missing(self) -> None:
        nested = os.path.join(self._tmp_dir, "sub", "dir")
        storage = LocalFileStorage(base_dir=nested)

        path = storage.save("test.csv", b"data")

        assert os.path.isfile(path)
