from __future__ import annotations

import base64
from io import BytesIO

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd

from src.domain.entities.chart_result import ChartResult
from src.domain.repositories.chart_generator import ChartGenerator
from src.shared.exceptions.base import DomainError

matplotlib.use("Agg")


class ChartGenerationError(DomainError):
    pass


class MatplotlibChartGenerator(ChartGenerator):

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
        fig, ax = plt.subplots(figsize=(8, 4))
        null_counts.plot.bar(ax=ax, color="#e74c3c")
        ax.set_title("Valores nulos por columna")
        ax.set_ylabel("Cantidad de nulos")
        ax.set_xlabel("Columna")
        fig.tight_layout()
        return ChartResult(
            chart_type="nulls_per_column",
            title="Valores nulos por columna",
            columns=null_counts.index.tolist(),
            image_base64=self._figure_to_base64(fig),
        )

    def _dtype_distribution(self, df: pd.DataFrame) -> ChartResult:
        dtype_counts = df.dtypes.astype(str).value_counts()
        fig, ax = plt.subplots(figsize=(6, 4))
        dtype_counts.plot.bar(ax=ax, color="#3498db")
        ax.set_title("Distribución de tipos de columna")
        ax.set_ylabel("Cantidad")
        ax.set_xlabel("Tipo")
        fig.tight_layout()
        return ChartResult(
            chart_type="dtype_distribution",
            title="Distribución de tipos de columna",
            columns=list(df.columns),
            image_base64=self._figure_to_base64(fig),
        )

    def _histogram(self, df: pd.DataFrame, col: str) -> ChartResult:
        fig, ax = plt.subplots(figsize=(6, 4))
        df[col].dropna().plot.hist(ax=ax, bins=20, color="#2ecc71", edgecolor="white")
        ax.set_title(f"Histograma: {col}")
        ax.set_xlabel(col)
        ax.set_ylabel("Frecuencia")
        fig.tight_layout()
        return ChartResult(
            chart_type="histogram",
            title=f"Histograma: {col}",
            columns=[col],
            image_base64=self._figure_to_base64(fig),
        )

    def _top_values(self, df: pd.DataFrame, col: str, top_n: int = 10) -> ChartResult:
        counts = df[col].value_counts().head(top_n)
        fig, ax = plt.subplots(figsize=(6, 4))
        counts.plot.barh(ax=ax, color="#9b59b6")
        ax.set_title(f"Top valores: {col}")
        ax.set_xlabel("Frecuencia")
        ax.set_ylabel(col)
        fig.tight_layout()
        return ChartResult(
            chart_type="top_values",
            title=f"Top valores: {col}",
            columns=[col],
            image_base64=self._figure_to_base64(fig),
        )
