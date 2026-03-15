from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from src.domain.value_objects.executed_step import ExecutedStep
from src.domain.value_objects.transformation_step import TransformationStep


@dataclass(frozen=True)
class TransformationOutput:
    csv_bytes: bytes
    executed_steps: list[ExecutedStep]
    row_count: int
    column_count: int
    null_count: int


class TransformationEngine(ABC):

    @abstractmethod
    def execute(
        self, file_path: str, steps: list[TransformationStep],
    ) -> TransformationOutput: ...
