from dataclasses import dataclass


@dataclass(frozen=True)
class ColumnProfile:
    name: str
    dtype: str
    null_count: int
    unique_count: int
