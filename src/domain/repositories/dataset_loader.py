from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class RawDatasetData:
    columns: list[str]
    row_count: int
    dtypes: dict[str, str]
    null_counts: dict[str, int]
    unique_counts: dict[str, int]


class DatasetLoader(ABC):

    @abstractmethod
    def load(self, file_path: str) -> RawDatasetData: ...
