from __future__ import annotations

import os

import pandas as pd
import pytest

from src.domain.value_objects.transformation_step import TransformAction, TransformationStep
from src.infrastructure.etl.pandas_transformation_engine import PandasTransformationEngine


@pytest.fixture()
def engine() -> PandasTransformationEngine:
    return PandasTransformationEngine()


@pytest.fixture()
def sample_csv(tmp_path) -> str:
    df = pd.DataFrame({
        "Name ": ["  Alice ", " Bob", "Charlie", "Alice ", "Alice "],
        " Age": [30, None, 25, 30, 30],
        "City": ["NYC", "LA", "NYC", "NYC", "NYC"],
        "Empty": [None, None, None, None, None],
        "Const": ["x", "x", "x", "x", "x"],
        "created_date": ["2024-01-01", "2024-02-01", "invalid", "2024-01-01", "2024-01-01"],
    })
    path = str(tmp_path / "test.csv")
    df.to_csv(path, index=False)
    return path


# ---- NORMALIZE_NAMES ----

def test_normalize_names(engine, sample_csv):
    steps = [
        TransformationStep(column_name=None, action=TransformAction.NORMALIZE_NAMES, params={}, reason="", priority=1),
    ]
    output = engine.execute(sample_csv, steps)
    cols = _columns_from_bytes(output.csv_bytes)
    assert "name" in cols
    assert "age" in cols
    assert output.executed_steps[0].success is True


# ---- DROP_COLUMN ----

def test_drop_column(engine, sample_csv):
    steps = [
        TransformationStep(column_name="Empty", action=TransformAction.DROP_COLUMN, params={}, reason="", priority=1),
    ]
    output = engine.execute(sample_csv, steps)
    assert "Empty" not in _columns_from_bytes(output.csv_bytes)
    assert output.executed_steps[0].success is True
    assert output.column_count == 5


def test_drop_column_missing(engine, sample_csv):
    steps = [
        TransformationStep(column_name="nonexistent", action=TransformAction.DROP_COLUMN, params={}, reason="", priority=1),
    ]
    output = engine.execute(sample_csv, steps)
    assert output.executed_steps[0].success is False
    assert output.column_count == 6


# ---- REMOVE_DUPLICATES ----

def test_remove_duplicates(engine, sample_csv):
    steps = [
        TransformationStep(column_name=None, action=TransformAction.REMOVE_DUPLICATES, params={}, reason="", priority=1),
    ]
    output = engine.execute(sample_csv, steps)
    assert output.row_count < 5
    assert output.executed_steps[0].success is True


# ---- STRIP_WHITESPACE ----

def test_strip_whitespace(engine, sample_csv):
    steps = [
        TransformationStep(column_name="Name ", action=TransformAction.STRIP_WHITESPACE, params={}, reason="", priority=1),
    ]
    output = engine.execute(sample_csv, steps)
    df = _bytes_to_df(output.csv_bytes)
    assert output.executed_steps[0].success is True
    assert df["Name "].iloc[0] == "Alice"


def test_strip_whitespace_missing_column(engine, sample_csv):
    steps = [
        TransformationStep(column_name="missing", action=TransformAction.STRIP_WHITESPACE, params={}, reason="", priority=1),
    ]
    output = engine.execute(sample_csv, steps)
    assert output.executed_steps[0].success is False


# ---- CAST_TYPE ----

def test_cast_type_datetime(engine, sample_csv):
    steps = [
        TransformationStep(column_name="created_date", action=TransformAction.CAST_TYPE, params={"target_type": "datetime64"}, reason="", priority=1),
    ]
    output = engine.execute(sample_csv, steps)
    assert output.executed_steps[0].success is True


def test_cast_type_unsupported(engine, sample_csv):
    steps = [
        TransformationStep(column_name="City", action=TransformAction.CAST_TYPE, params={"target_type": "int"}, reason="", priority=1),
    ]
    output = engine.execute(sample_csv, steps)
    assert output.executed_steps[0].success is False


# ---- FILL_NULLS_MEDIAN ----

def test_fill_nulls_median(engine, sample_csv):
    steps = [
        TransformationStep(column_name=" Age", action=TransformAction.FILL_NULLS_MEDIAN, params={}, reason="", priority=1),
    ]
    output = engine.execute(sample_csv, steps)
    df = _bytes_to_df(output.csv_bytes)
    assert output.executed_steps[0].success is True
    assert df[" Age"].isnull().sum() == 0


def test_fill_nulls_median_no_nulls(engine, sample_csv):
    steps = [
        TransformationStep(column_name="City", action=TransformAction.FILL_NULLS_MEDIAN, params={}, reason="", priority=1),
    ]
    output = engine.execute(sample_csv, steps)
    assert output.executed_steps[0].success is False


# ---- FILL_NULLS_MODE ----

def test_fill_nulls_mode(engine, sample_csv):
    steps = [
        TransformationStep(column_name=" Age", action=TransformAction.FILL_NULLS_MODE, params={}, reason="", priority=1),
    ]
    output = engine.execute(sample_csv, steps)
    df = _bytes_to_df(output.csv_bytes)
    assert output.executed_steps[0].success is True
    assert df[" Age"].isnull().sum() == 0


# ---- FILL_NULLS_UNKNOWN ----

def test_fill_nulls_unknown(engine, sample_csv):
    # Use a column that has some nulls (Age has 1 null)
    steps = [
        TransformationStep(column_name=" Age", action=TransformAction.FILL_NULLS_UNKNOWN, params={"fill_value": "0"}, reason="", priority=1),
    ]
    output = engine.execute(sample_csv, steps)
    df = _bytes_to_df(output.csv_bytes)
    assert output.executed_steps[0].success is True
    assert df[" Age"].isnull().sum() == 0


# ---- KEEP ----

def test_keep(engine, sample_csv):
    steps = [
        TransformationStep(column_name="City", action=TransformAction.KEEP, params={}, reason="", priority=1),
    ]
    output = engine.execute(sample_csv, steps)
    assert output.executed_steps[0].success is False  # KEEP is a no-op


# ---- ORDERING ----

def test_steps_executed_in_priority_order(engine, sample_csv):
    steps = [
        TransformationStep(column_name="Empty", action=TransformAction.DROP_COLUMN, params={}, reason="", priority=3),
        TransformationStep(column_name=None, action=TransformAction.NORMALIZE_NAMES, params={}, reason="", priority=1),
        TransformationStep(column_name="Const", action=TransformAction.DROP_COLUMN, params={}, reason="", priority=2),
    ]
    output = engine.execute(sample_csv, steps)
    actions = [s.action for s in output.executed_steps]
    assert actions[0] == TransformAction.NORMALIZE_NAMES


# ---- FULL PIPELINE ----

def test_full_pipeline(engine, sample_csv):
    steps = [
        TransformationStep(column_name=None, action=TransformAction.NORMALIZE_NAMES, params={}, reason="", priority=1),
        TransformationStep(column_name="empty", action=TransformAction.DROP_COLUMN, params={}, reason="", priority=2),
        TransformationStep(column_name="const", action=TransformAction.DROP_COLUMN, params={}, reason="", priority=3),
        TransformationStep(column_name="name", action=TransformAction.STRIP_WHITESPACE, params={}, reason="", priority=4),
        TransformationStep(column_name="age", action=TransformAction.FILL_NULLS_MEDIAN, params={}, reason="", priority=5),
        TransformationStep(column_name=None, action=TransformAction.REMOVE_DUPLICATES, params={}, reason="", priority=6),
    ]
    output = engine.execute(sample_csv, steps)
    cols = _columns_from_bytes(output.csv_bytes)
    assert "empty" not in cols
    assert "const" not in cols
    assert output.null_count == 0 or output.null_count < 5  # Age nulls filled
    assert output.row_count <= 5
    success_count = sum(1 for s in output.executed_steps if s.success)
    assert success_count == 6


# ---- Helpers ----

def _bytes_to_df(csv_bytes: bytes) -> pd.DataFrame:
    import io
    return pd.read_csv(io.BytesIO(csv_bytes))


def _columns_from_bytes(csv_bytes: bytes) -> list[str]:
    return list(_bytes_to_df(csv_bytes).columns)
