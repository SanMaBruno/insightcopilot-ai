from __future__ import annotations

from dataclasses import dataclass, field

from src.domain.value_objects.document_chunk import DocumentChunk


@dataclass
class ContextualAnswer:
    dataset_id: str
    question: str
    answer: str
    sources: list[DocumentChunk] = field(default_factory=list)
