from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class QualityScore:
    completeness: float
    consistency: float
    uniqueness: float
    validity: float
    overall: float
