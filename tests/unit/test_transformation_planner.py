from src.application.services.transformation_planner import generate_plan_steps
from src.domain.value_objects.column_classification import ColumnClassification, ColumnRole
from src.domain.value_objects.transformation_step import TransformAction


def _make_col(
    name: str,
    role: ColumnRole,
    dtype: str = "object",
    null_ratio: float = 0.0,
) -> ColumnClassification:
    return ColumnClassification(
        column_name=name, dtype=dtype, role=role,
        null_ratio=null_ratio, unique_ratio=0.5, reason="test",
    )


class TestTransformationPlanner:

    def test_empty_column_dropped_in_both_strategies(self) -> None:
        cols = [_make_col("empty", ColumnRole.EMPTY)]

        for strategy in ("conservative", "aggressive"):
            steps = generate_plan_steps(cols, 0, strategy)
            actions = [s.action for s in steps if s.column_name == "empty"]
            assert TransformAction.DROP_COLUMN in actions

    def test_constant_column_dropped(self) -> None:
        cols = [_make_col("const", ColumnRole.CONSTANT)]

        steps = generate_plan_steps(cols, 0, "conservative")
        actions = [s.action for s in steps if s.column_name == "const"]

        assert TransformAction.DROP_COLUMN in actions

    def test_high_null_kept_conservative(self) -> None:
        cols = [_make_col("notes", ColumnRole.HIGH_NULL, null_ratio=0.7)]

        steps = generate_plan_steps(cols, 0, "conservative")
        actions = [s.action for s in steps if s.column_name == "notes"]

        assert TransformAction.KEEP in actions

    def test_high_null_dropped_aggressive(self) -> None:
        cols = [_make_col("notes", ColumnRole.HIGH_NULL, null_ratio=0.7)]

        steps = generate_plan_steps(cols, 0, "aggressive")
        actions = [s.action for s in steps if s.column_name == "notes"]

        assert TransformAction.DROP_COLUMN in actions

    def test_identifier_kept_conservative(self) -> None:
        cols = [_make_col("user_id", ColumnRole.IDENTIFIER, "int64")]

        steps = generate_plan_steps(cols, 0, "conservative")
        col_steps = [s for s in steps if s.column_name == "user_id"]

        assert not any(s.action == TransformAction.DROP_COLUMN for s in col_steps)

    def test_identifier_dropped_aggressive(self) -> None:
        cols = [_make_col("user_id", ColumnRole.IDENTIFIER, "int64")]

        steps = generate_plan_steps(cols, 0, "aggressive")
        actions = [s.action for s in steps if s.column_name == "user_id"]

        assert TransformAction.DROP_COLUMN in actions

    def test_valuable_numeric_with_nulls_fills_median(self) -> None:
        cols = [_make_col("age", ColumnRole.VALUABLE_NUMERIC, "float64", null_ratio=0.1)]

        steps = generate_plan_steps(cols, 0, "conservative")
        actions = [s.action for s in steps if s.column_name == "age"]

        assert TransformAction.FILL_NULLS_MEDIAN in actions

    def test_valuable_numeric_no_nulls_no_step(self) -> None:
        cols = [_make_col("age", ColumnRole.VALUABLE_NUMERIC, "float64", null_ratio=0.0)]

        steps = generate_plan_steps(cols, 0, "conservative")
        col_steps = [s for s in steps if s.column_name == "age"]

        assert len(col_steps) == 0

    def test_valuable_categorical_fills_mode_conservative(self) -> None:
        cols = [_make_col("city", ColumnRole.VALUABLE_CATEGORICAL, null_ratio=0.05)]

        steps = generate_plan_steps(cols, 0, "conservative")
        actions = [s.action for s in steps if s.column_name == "city"]

        assert TransformAction.FILL_NULLS_MODE in actions

    def test_valuable_categorical_fills_unknown_aggressive(self) -> None:
        cols = [_make_col("city", ColumnRole.VALUABLE_CATEGORICAL, null_ratio=0.05)]

        steps = generate_plan_steps(cols, 0, "aggressive")
        actions = [s.action for s in steps if s.column_name == "city"]

        assert TransformAction.FILL_NULLS_UNKNOWN in actions

    def test_date_candidate_casts(self) -> None:
        cols = [_make_col("fecha", ColumnRole.DATE_CANDIDATE)]

        steps = generate_plan_steps(cols, 0, "conservative")
        cast_steps = [s for s in steps if s.column_name == "fecha" and s.action == TransformAction.CAST_TYPE]

        assert len(cast_steps) == 1
        assert cast_steps[0].params["target_type"] == "datetime64"

    def test_strip_whitespace_for_categorical(self) -> None:
        cols = [_make_col("city", ColumnRole.VALUABLE_CATEGORICAL)]

        steps = generate_plan_steps(cols, 0, "conservative")
        strip_steps = [s for s in steps if s.action == TransformAction.STRIP_WHITESPACE]

        assert len(strip_steps) == 1

    def test_duplicates_kept_conservative(self) -> None:
        cols = [_make_col("a", ColumnRole.VALUABLE_NUMERIC, "int64")]

        steps = generate_plan_steps(cols, 10, "conservative")
        dup_steps = [s for s in steps if s.column_name is None]

        assert len(dup_steps) == 1
        assert dup_steps[0].action == TransformAction.KEEP
        assert "duplicada" in dup_steps[0].reason

    def test_duplicates_removed_aggressive(self) -> None:
        cols = [_make_col("a", ColumnRole.VALUABLE_NUMERIC, "int64")]

        steps = generate_plan_steps(cols, 10, "aggressive")
        dup_steps = [s for s in steps if s.action == TransformAction.REMOVE_DUPLICATES]

        assert len(dup_steps) == 1

    def test_priorities_are_sequential(self) -> None:
        cols = [
            _make_col("empty", ColumnRole.EMPTY),
            _make_col("age", ColumnRole.VALUABLE_NUMERIC, "float64", null_ratio=0.1),
        ]

        steps = generate_plan_steps(cols, 5, "aggressive")
        priorities = [s.priority for s in steps]

        assert priorities == sorted(priorities)
        assert len(set(priorities)) == len(priorities)
