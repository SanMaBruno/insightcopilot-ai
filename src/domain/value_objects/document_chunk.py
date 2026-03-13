from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DocumentChunk:
    """Fragmento de un documento indexado."""

    source: str
    content: str
    chunk_index: int
