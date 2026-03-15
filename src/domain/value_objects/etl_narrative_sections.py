from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EtlNarrativeSections:
    resumen: str
    calidad_original: str
    transformaciones: str
    resultado: str
    recomendaciones: str
