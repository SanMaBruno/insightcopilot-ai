from __future__ import annotations

from src.domain.entities.curated_result import CuratedResult

_SYSTEM_PROMPT = (
    "Eres un analista de datos senior. Tu trabajo es generar una narrativa profesional "
    "que DESCRIBA y CONTEXTUALICE un proceso ETL que YA fue ejecutado.\n\n"
    "REGLAS ESTRICTAS:\n"
    "- Usa ÚNICAMENTE la información proporcionada en el contexto.\n"
    "- NO inventes datos, cifras ni métricas que no estén en el contexto.\n"
    "- NO sugieras transformaciones adicionales ni decisiones ETL.\n"
    "- Tu rol es SOLO describir lo que ocurrió, NUNCA decidir.\n"
    "- Responde en español.\n\n"
    "FORMATO DE RESPUESTA (usa exactamente estos encabezados):\n"
    "## RESUMEN\n"
    "(Un párrafo con la visión general del proceso ETL)\n\n"
    "## CALIDAD_ORIGINAL\n"
    "(Descripción del estado original del dataset antes de las transformaciones)\n\n"
    "## TRANSFORMACIONES\n"
    "(Descripción de cada transformación aplicada y su impacto)\n\n"
    "## RESULTADO\n"
    "(Métricas finales y comparación antes/después)\n\n"
    "## RECOMENDACIONES\n"
    "(Observaciones generales sobre el resultado obtenido)\n"
)


def build_system_prompt() -> str:
    return _SYSTEM_PROMPT


def build_user_prompt(result: CuratedResult) -> str:
    lines: list[str] = []

    lines.append("== ETL CONTEXT ==")
    lines.append(f"Dataset ID: {result.dataset_id}")
    lines.append(f"ETL Run ID: {result.etl_run_id}")
    lines.append(f"Estrategia: {result.strategy}")
    lines.append(f"Modo de ejecución: {result.execution_mode}")
    lines.append("")

    lines.append("Métricas antes/después:")
    lines.append(f"  Filas: {result.original_row_count} → {result.curated_row_count}")
    lines.append(f"  Columnas: {result.original_column_count} → {result.curated_column_count}")
    lines.append(f"  Nulos: {result.original_null_count} → {result.curated_null_count}")
    lines.append(f"  Tiempo de ejecución: {result.execution_time_ms}ms")
    lines.append("")

    lines.append("Pasos ejecutados:")
    for step in result.executed_steps:
        col = step.column_name if step.column_name else "global"
        status = "OK" if step.success else "OMITIDO"
        lines.append(
            f"  - [{status}] {step.action.value} en '{col}': {step.detail}"
        )
    lines.append("")

    lines.append("Genera la narrativa basándote exclusivamente en esta información.")
    return "\n".join(lines)
