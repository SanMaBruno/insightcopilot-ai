from __future__ import annotations

from src.domain.entities.dataset_insight import DatasetInsightReport
from src.domain.entities.dataset_profile import DatasetProfile
from src.domain.value_objects.document_chunk import DocumentChunk

_MAX_CONTEXT_CHARS = 6000

_SYSTEM_PROMPT = (
    "Eres un analista de datos senior. Tu trabajo es responder preguntas "
    "combinando información analítica de un dataset con documentos de contexto.\n\n"
    "REGLAS ESTRICTAS:\n"
    "- Usa ÚNICAMENTE la información proporcionada (perfil del dataset, insights "
    "y fragmentos documentales).\n"
    "- NO inventes datos, cifras ni tendencias que no estén en el contexto.\n"
    "- Si la información es insuficiente, indícalo explícitamente.\n"
    "- Cuando uses información de un fragmento documental, indica la fuente.\n"
    "- Responde en español.\n"
)


def build_rag_system_prompt() -> str:
    return _SYSTEM_PROMPT


def build_rag_user_prompt(
    dataset_name: str,
    profile: DatasetProfile,
    report: DatasetInsightReport,
    chunks: list[DocumentChunk],
    question: str,
) -> str:
    lines: list[str] = []

    # --- Contexto analítico ---
    lines.append("=== CONTEXTO ANALÍTICO ===")
    lines.append(f"Dataset: {dataset_name}")
    lines.append(f"Filas: {profile.row_count}  |  Columnas: {profile.column_count}")
    lines.append("")

    for col in profile.columns:
        lines.append(
            f"  - {col.name} (tipo: {col.dtype}, "
            f"nulos: {col.null_count}, únicos: {col.unique_count})"
        )
    lines.append("")

    if report.insights:
        lines.append("Insights:")
        for insight in report.insights:
            lines.append(f"  - [{insight.category}] {insight.message}")
        lines.append("")

    if report.warnings:
        lines.append("Advertencias:")
        for w in report.warnings:
            lines.append(f"  - {w}")
        lines.append("")

    # --- Fragmentos documentales (limitados) ---
    if chunks:
        lines.append("=== CONTEXTO DOCUMENTAL ===")
        char_budget = _MAX_CONTEXT_CHARS
        for chunk in chunks:
            fragment = f"[{chunk.source} #{chunk.chunk_index}]\n{chunk.content}"
            if len(fragment) > char_budget:
                break
            lines.append(fragment)
            lines.append("")
            char_budget -= len(fragment)

    # --- Pregunta ---
    lines.append("=== PREGUNTA ===")
    lines.append(question)

    return "\n".join(lines)
