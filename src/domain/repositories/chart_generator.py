from __future__ import annotations

from abc import ABC, abstractmethod

from src.domain.entities.chart_result import ChartResult


class ChartGenerator(ABC):

    @abstractmethod
    def generate(self, file_path: str) -> list[ChartResult]: ...
