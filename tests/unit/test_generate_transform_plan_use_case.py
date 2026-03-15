from unittest.mock import MagicMock

from src.application.use_cases.generate_transform_plan_use_case import (
    GenerateTransformPlanUseCase,
)
from src.domain.entities.dataset import Dataset
from src.domain.entities.transformation_plan import PlanStatus
from src.domain.repositories.dataset_loader import RawDatasetData
from src.domain.value_objects.transformation_step import TransformAction


def _make_dataset() -> Dataset:
    return Dataset(name="test", file_path="/tmp/test.csv", source_type="csv", id="ds-1")


def _make_raw() -> RawDatasetData:
    return RawDatasetData(
        columns=["age", "empty_col"],
        row_count=100,
        dtypes={"age": "float64", "empty_col": "object"},
        null_counts={"age": 10, "empty_col": 100},
        unique_counts={"age": 60, "empty_col": 0},
        duplicate_row_count=3,
    )


class TestGenerateTransformPlanUseCase:

    def test_returns_plan_with_proposed_status(self) -> None:
        repo = MagicMock()
        repo.get_by_id.return_value = _make_dataset()
        loader = MagicMock()
        loader.load.return_value = _make_raw()

        plan = GenerateTransformPlanUseCase(repository=repo, loader=loader).execute(
            dataset_id="ds-1",
            etl_run_id="run-1",
            quality_assessment_id="qa-1",
            strategy="conservative",
        )

        assert plan.dataset_id == "ds-1"
        assert plan.etl_run_id == "run-1"
        assert plan.quality_assessment_id == "qa-1"
        assert plan.status == PlanStatus.PROPOSED
        assert plan.strategy == "conservative"
        assert len(plan.steps) > 0

    def test_conservative_drops_empty_keeps_duplicates(self) -> None:
        repo = MagicMock()
        repo.get_by_id.return_value = _make_dataset()
        loader = MagicMock()
        loader.load.return_value = _make_raw()

        plan = GenerateTransformPlanUseCase(repository=repo, loader=loader).execute(
            dataset_id="ds-1",
            etl_run_id="run-1",
            quality_assessment_id="qa-1",
            strategy="conservative",
        )

        actions = {s.column_name: s.action for s in plan.steps}
        assert actions.get("empty_col") == TransformAction.DROP_COLUMN
        assert actions.get("age") == TransformAction.FILL_NULLS_MEDIAN

        dup_steps = [s for s in plan.steps if s.column_name is None]
        assert any(s.action == TransformAction.KEEP for s in dup_steps)

    def test_aggressive_removes_duplicates(self) -> None:
        repo = MagicMock()
        repo.get_by_id.return_value = _make_dataset()
        loader = MagicMock()
        loader.load.return_value = _make_raw()

        plan = GenerateTransformPlanUseCase(repository=repo, loader=loader).execute(
            dataset_id="ds-1",
            etl_run_id="run-1",
            quality_assessment_id="qa-1",
            strategy="aggressive",
        )

        dup_steps = [s for s in plan.steps if s.action == TransformAction.REMOVE_DUPLICATES]
        assert len(dup_steps) == 1
