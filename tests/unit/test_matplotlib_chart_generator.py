from __future__ import annotations

import base64
import os

import pytest

from src.infrastructure.files.matplotlib_chart_generator import (
    ChartGenerationError,
    MatplotlibChartGenerator,
)

_CSV_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "data", "sample", "test_data.csv")
)


class TestMatplotlibChartGenerator:

    def setup_method(self) -> None:
        self.generator = MatplotlibChartGenerator()

    def test_generates_expected_chart_types(self) -> None:
        charts = self.generator.generate(_CSV_PATH)
        types = [c.chart_type for c in charts]

        # test_data.csv: name(obj), age(num con nulos), city(obj con nulos)
        assert "nulls_per_column" in types
        assert "dtype_distribution" in types
        assert "histogram" in types
        assert "top_values" in types

    def test_generates_histogram_for_numeric_columns(self) -> None:
        charts = self.generator.generate(_CSV_PATH)
        histograms = [c for c in charts if c.chart_type == "histogram"]

        assert len(histograms) == 1
        assert histograms[0].columns == ["age"]

    def test_generates_top_values_for_categorical_columns(self) -> None:
        charts = self.generator.generate(_CSV_PATH)
        top_values = [c for c in charts if c.chart_type == "top_values"]

        assert len(top_values) == 2
        cols = {c.columns[0] for c in top_values}
        assert cols == {"name", "city"}

    def test_image_base64_is_valid_png(self) -> None:
        charts = self.generator.generate(_CSV_PATH)

        for chart in charts:
            raw = base64.b64decode(chart.image_base64)
            # PNG magic bytes
            assert raw[:8] == b"\x89PNG\r\n\x1a\n"

    def test_each_chart_has_title_and_columns(self) -> None:
        charts = self.generator.generate(_CSV_PATH)

        for chart in charts:
            assert chart.title
            assert len(chart.columns) >= 1

    def test_raises_on_missing_file(self) -> None:
        with pytest.raises(ChartGenerationError, match="no encontrado"):
            self.generator.generate("/no/existe.csv")
