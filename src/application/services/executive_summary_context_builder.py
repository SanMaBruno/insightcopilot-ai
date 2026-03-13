from __future__ import annotations

from src.domain.entities.dataset_insight import DatasetInsightReport
from src.domain.entities.dataset_profile import DatasetProfile

_SYSTEM_PROMPT = (
    "Eres un analista de datos senior. Tu trabajo es generar resúmenes ejecutivos "
    "claros, precisos y accionables a partir de información analítica ya procesada.\n\n"
    "REGLAS ESTRICTAS:\n"
    "- Usa ÚNICAMENTE la información proporcionada en el contexto.\n"
    "- NO inventes datos, cifras, tendencias ni columnas que no estén en el contexto.\n"
    "- Si la información es insuficiente, indícalo explícitamente.\n"
    "- No menciones que trabajas con un 'perfil' o 'insights'; habla del dataset directamente.\n"
    "- Responde en español.\n"
)


def build_system_prompt(audience: str, tone: str, max_paragraphs: int) -> str:
    return (
        f"{_SYSTEM_PROMPT}"
        f"AUDIENCIA: {audience}\n"
        f"TONO: {tone}\n"
        f"EXTENSIÓN MÁXIMA: {max_paragraphs} párrafos.\n"
    )


def build_user_prompt(
    dataset_name: str,
    profile: DatasetProfile,
    report: DatasetInsightReport,
) -> str:
    lines: list[str] = []

    lines.append(f"Dataset: {dataset_name}")
    lines.append(f"Filas: {profile.row_count}")
    lines.append(f"Columnas: {profile.column_count}")
    lines.append("")

    lines.append("Detalle de columnas:")
    for col in profile.columns:
        lines.append(
            f"  - {col.name} (tipo: {col.dtype}, "
            f"nulos: {col.null_count}, únicos: {col.unique_count})"
        )
    lines.append("")

    if report.insights:
        lines.append("Insights detectados:")
        for insight in report.insights:
            lines.append(f"  - [{insight.category}] {insight.message}")
        lines.append("")

    if report.warnings:
        lines.append("Advertencias:")
        for w in report.warnings:
            lines.append(f"  - {w}")
        lines.append("")

    lines.append("Genera un resumen ejecutivo basado exclusivamente en esta información.")
    return "\n".join(lines)
