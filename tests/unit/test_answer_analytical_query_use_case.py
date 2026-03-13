from __future__ import annotations

import os

import pytest

from src.application.use_cases.answer_analytical_query_use_case import (
    AnswerAnalyticalQueryUseCase,
)
from src.application.use_cases.get_dataset_by_id_use_case import DatasetNotFoundError
from src.domain.entities.dataset import Dataset
from src.infrastructure.files.csv_dataset_loader import CsvDatasetLoader
from src.infrastructure.persistence.in_memory_dataset_repository import (
    InMemoryDatasetRepository,
)

_CSV_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "data", "sample", "test_data.csv")
)


class TestAnswerAnalyticalQueryUseCase:

    def setup_method(self) -> None:
        self.repo = InMemoryDatasetRepository()
        self.loader = CsvDatasetLoader()
        self.use_case = AnswerAnalyticalQueryUseCase(
            repository=self.repo, loader=self.loader
        )

    def test_answers_summary_question(self) -> None:
        ds = Dataset(name="test", file_path=_CSV_PATH, source_type="csv")
        self.repo.save(ds)

        answer = self.use_case.execute(ds.id, "Dame un resumen general")

        assert answer.dataset_id == ds.id
        assert answer.intent == "resumen"
        assert "3 filas" in answer.answer

    def test_answers_nulls_question(self) -> None:
        ds = Dataset(name="test", file_path=_CSV_PATH, source_type="csv")
        self.repo.save(ds)

        answer = self.use_case.execute(ds.id, "¿Qué columnas tienen nulos?")

        assert answer.intent == "nulos"
        assert len(answer.supporting_data) > 0

    def test_raises_when_dataset_not_found(self) -> None:
        with pytest.raises(DatasetNotFoundError):
            self.use_case.execute("nonexistent", "resumen")
