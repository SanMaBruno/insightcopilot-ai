from __future__ import annotations

import base64
from io import BytesIO

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.domain.entities.chart_result import (
    ChartResult,
    ChartSeries,
    InteractiveChartSpec,
)
from src.domain.repositories.chart_generator import ChartGenerator
from src.shared.exceptions.base import DomainError

matplotlib.use("Agg")


class ChartGenerationError(DomainError):
    pass


class MatplotlibChartGenerator(ChartGenerator):
    _PALETTE = {
        "nulls_per_column": "#e45f52",
        "dtype_distribution": "#3d6bf2",
        "histogram": "#21a67a",
        "top_values": "#d06dd8",
    }

    def generate(self, file_path: str) -> list[ChartResult]:
        try:
            df = pd.read_csv(file_path)
        except FileNotFoundError as exc:
            raise ChartGenerationError(f"Archivo no encontrado: {file_path}") from exc
        except Exception as exc:
            raise ChartGenerationError(f"Error al leer archivo: {exc}") from exc

        charts: list[ChartResult] = []

        null_counts = df.isnull().sum()
        if null_counts.sum() > 0:
            charts.append(self._nulls_per_column(null_counts))

        charts.append(self._dtype_distribution(df))

        numeric_cols = df.select_dtypes(include="number").columns.tolist()
        for col in numeric_cols:
            charts.append(self._histogram(df, col))

        categorical_cols = df.select_dtypes(exclude="number").columns.tolist()
        for col in categorical_cols:
            charts.append(self._top_values(df, col))

        return charts

    # ------------------------------------------------------------------
    # Helpers privados
    # ------------------------------------------------------------------

    def _figure_to_base64(self, fig: matplotlib.figure.Figure) -> str:
        buf = BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight", dpi=100)
        plt.close(fig)
        buf.seek(0)
        return base64.b64encode(buf.read()).decode("utf-8")

    def _nulls_per_column(self, null_counts: pd.Series) -> ChartResult:
        series = null_counts.astype(float)
        fig, ax = plt.subplots(figsize=(8, 4))
        series.plot.bar(ax=ax, color=self._PALETTE["nulls_per_column"])
        ax.set_title("Valores nulos por columna")
        ax.set_ylabel("Cantidad de nulos")
        ax.set_xlabel("Columna")
        fig.tight_layout()
        return ChartResult(
            chart_type="nulls_per_column",
            title="Valores nulos por columna",
            columns=null_counts.index.tolist(),
            image_base64=self._figure_to_base64(fig),
            interactive_spec=self._build_spec(
                chart_kind="column",
                subtitle="Comparativa por columna",
                categories=[str(label) for label in series.index.tolist()],
                series=[
                    ChartSeries(
                        name="Nulos",
                        data=series.tolist(),
                        color=self._PALETTE["nulls_per_column"],
                    )
                ],
                x_axis_label="Columna",
                y_axis_label="Cantidad de nulos",
                tooltip_suffix=" nulos",
                source_label="Dataset profile",
            ),
        )

    def _dtype_distribution(self, df: pd.DataFrame) -> ChartResult:
        dtype_counts = df.dtypes.astype(str).value_counts().astype(float)
        fig, ax = plt.subplots(figsize=(6, 4))
        dtype_counts.plot.bar(ax=ax, color=self._PALETTE["dtype_distribution"])
        ax.set_title("Distribución de tipos de columna")
        ax.set_ylabel("Cantidad")
        ax.set_xlabel("Tipo")
        fig.tight_layout()
        return ChartResult(
            chart_type="dtype_distribution",
            title="Distribución de tipos de columna",
            columns=list(df.columns),
            image_base64=self._figure_to_base64(fig),
            interactive_spec=self._build_spec(
                chart_kind="column",
                subtitle="Composición del dataset por tipo",
                categories=[str(label) for label in dtype_counts.index.tolist()],
                series=[
                    ChartSeries(
                        name="Columnas",
                        data=dtype_counts.tolist(),
                        color=self._PALETTE["dtype_distribution"],
                    )
                ],
                x_axis_label="Tipo de dato",
                y_axis_label="Cantidad de columnas",
                tooltip_suffix=" columnas",
                source_label="Schema overview",
            ),
        )

    def _histogram(self, df: pd.DataFrame, col: str) -> ChartResult:
        values = df[col].dropna()
        hist, edges = np.histogram(values, bins=20)
        categories = self._format_histogram_bins(edges)
        fig, ax = plt.subplots(figsize=(6, 4))
        values.plot.hist(
            ax=ax,
            bins=20,
            color=self._PALETTE["histogram"],
            edgecolor="white",
        )
        ax.set_title(f"Histograma: {col}")
        ax.set_xlabel(col)
        ax.set_ylabel("Frecuencia")
        fig.tight_layout()
        return ChartResult(
            chart_type="histogram",
            title=f"Histograma: {col}",
            columns=[col],
            image_base64=self._figure_to_base64(fig),
            interactive_spec=self._build_spec(
                chart_kind="column",
                subtitle="Distribución por intervalos",
                categories=categories,
                series=[
                    ChartSeries(
                        name=col,
                        data=hist.astype(float).tolist(),
                        color=self._PALETTE["histogram"],
                    )
                ],
                x_axis_label=col,
                y_axis_label="Frecuencia",
                tooltip_suffix=" registros",
                source_label="Numeric distribution",
            ),
        )

    def _top_values(self, df: pd.DataFrame, col: str, top_n: int = 10) -> ChartResult:
        counts = df[col].value_counts().head(top_n).astype(float)
        fig, ax = plt.subplots(figsize=(6, 4))
        counts.plot.barh(ax=ax, color=self._PALETTE["top_values"])
        ax.set_title(f"Top valores: {col}")
        ax.set_xlabel("Frecuencia")
        ax.set_ylabel(col)
        fig.tight_layout()
        return ChartResult(
            chart_type="top_values",
            title=f"Top valores: {col}",
            columns=[col],
            image_base64=self._figure_to_base64(fig),
            interactive_spec=self._build_spec(
                chart_kind="bar",
                subtitle=f"Top {min(top_n, len(counts))} categorías",
                categories=[str(label) for label in counts.index.tolist()],
                series=[
                    ChartSeries(
                        name="Frecuencia",
                        data=counts.tolist(),
                        color=self._PALETTE["top_values"],
                    )
                ],
                x_axis_label="Frecuencia",
                y_axis_label=col,
                tooltip_suffix=" registros",
                source_label="Categorical distribution",
            ),
        )

    def _build_spec(
        self,
        *,
        chart_kind: str,
        subtitle: str,
        categories: list[str],
        series: list[ChartSeries],
        x_axis_label: str,
        y_axis_label: str,
        tooltip_suffix: str,
        source_label: str,
    ) -> InteractiveChartSpec:
        return InteractiveChartSpec(
            chart_kind=chart_kind,
            subtitle=subtitle,
            categories=categories,
            series=series,
            x_axis_label=x_axis_label,
            y_axis_label=y_axis_label,
            tooltip_suffix=tooltip_suffix,
            source_label=source_label,
        )

    def _format_histogram_bins(self, edges: np.ndarray) -> list[str]:
        labels: list[str] = []
        for start, end in zip(edges[:-1], edges[1:]):
            labels.append(f"{start:.1f}–{end:.1f}")
        return labels
