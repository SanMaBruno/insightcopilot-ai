from __future__ import annotations

import sqlite3
from datetime import datetime, timezone

from src.domain.entities.dataset import Dataset
from src.domain.repositories.dataset_repository import DatasetRepository

_CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS datasets (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    file_path TEXT NOT NULL,
    source_type TEXT NOT NULL,
    created_at TEXT NOT NULL
)
"""


class SqliteDatasetRepository(DatasetRepository):

    def __init__(self, db_path: str) -> None:
        self._db_path = db_path
        self._init_db()

    # ------------------------------------------------------------------
    # Público
    # ------------------------------------------------------------------

    def save(self, dataset: Dataset) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO datasets (id, name, file_path, source_type, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    dataset.id,
                    dataset.name,
                    dataset.file_path,
                    dataset.source_type,
                    dataset.created_at.isoformat(),
                ),
            )

    def get_by_id(self, dataset_id: str) -> Dataset | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT id, name, file_path, source_type, created_at FROM datasets WHERE id = ?",
                (dataset_id,),
            ).fetchone()
        if row is None:
            return None
        return self._row_to_dataset(row)

    def list_all(self) -> list[Dataset]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT id, name, file_path, source_type, created_at FROM datasets "
                "ORDER BY created_at DESC"
            ).fetchall()
        return [self._row_to_dataset(r) for r in rows]

    # ------------------------------------------------------------------
    # Privado
    # ------------------------------------------------------------------

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self._db_path)

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(_CREATE_TABLE)

    @staticmethod
    def _row_to_dataset(row: tuple) -> Dataset:
        return Dataset(
            id=row[0],
            name=row[1],
            file_path=row[2],
            source_type=row[3],
            created_at=datetime.fromisoformat(row[4]).replace(tzinfo=timezone.utc),
        )
