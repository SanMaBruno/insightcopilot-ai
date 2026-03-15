from __future__ import annotations

import pandas as pd

from src.domain.repositories.dataset_loader import DatasetLoader, RawDatasetData
from src.shared.exceptions.base import DomainError


class FileLoadError(DomainError):
    pass


class CsvDatasetLoader(DatasetLoader):

    def load(self, file_path: str) -> RawDatasetData:
        try:
            df = pd.read_csv(file_path)
        except FileNotFoundError as exc:
            raise FileLoadError(f"Archivo no encontrado: {file_path}") from exc
        except pd.errors.ParserError as exc:
            raise FileLoadError(f"Formato CSV inválido: {file_path}") from exc
        except Exception as exc:
            raise FileLoadError(f"Error al leer archivo: {exc}") from exc

        return RawDatasetData(
            columns=list(df.columns),
            row_count=len(df),
            dtypes={col: str(dtype) for col, dtype in df.dtypes.items()},
            null_counts={col: int(count) for col, count in df.isnull().sum().items()},
            unique_counts={col: int(count) for col, count in df.nunique().items()},
            duplicate_row_count=int(df.duplicated().sum()),
        )
