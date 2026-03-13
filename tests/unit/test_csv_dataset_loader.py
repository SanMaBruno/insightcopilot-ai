import os

import pytest

from src.infrastructure.files.csv_dataset_loader import CsvDatasetLoader, FileLoadError

SAMPLE_CSV = os.path.join(os.path.dirname(__file__), "..", "..", "data", "sample", "test_data.csv")


class TestCsvDatasetLoader:

    def setup_method(self) -> None:
        self.loader = CsvDatasetLoader()

    def test_loads_valid_csv(self) -> None:
        raw = self.loader.load(SAMPLE_CSV)

        assert raw.row_count == 3
        assert raw.columns == ["name", "age", "city"]
        assert len(raw.dtypes) == 3
        assert raw.null_counts["age"] == 1
        assert raw.null_counts["city"] == 1
        assert raw.null_counts["name"] == 0
        assert raw.unique_counts["name"] == 3
        assert raw.unique_counts["city"] == 2

    def test_raises_on_missing_file(self) -> None:
        with pytest.raises(FileLoadError, match="no encontrado"):
            self.loader.load("/nonexistent/path.csv")
