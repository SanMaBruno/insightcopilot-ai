from __future__ import annotations

import os
import re
from uuid import uuid4

from src.domain.repositories.file_storage import FileStorage


class LocalFileStorage(FileStorage):

    def __init__(self, base_dir: str) -> None:
        self._base_dir = base_dir

    def save(self, filename: str, content: bytes) -> str:
        os.makedirs(self._base_dir, exist_ok=True)
        safe_name = self._sanitize(filename)
        unique_name = f"{uuid4().hex[:8]}_{safe_name}"
        full_path = os.path.join(self._base_dir, unique_name)
        with open(full_path, "wb") as f:
            f.write(content)
        return os.path.abspath(full_path)

    @staticmethod
    def _sanitize(filename: str) -> str:
        name = os.path.basename(filename)
        return re.sub(r"[^\w.\-]", "_", name)
