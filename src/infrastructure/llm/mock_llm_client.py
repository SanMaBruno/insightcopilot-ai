from __future__ import annotations

import re

from src.domain.llm_client import LlmClient


def _extract_value(pattern: str, text: str, default: str) -> str:
    match = re.search(pattern, text, re.MULTILINE)
    if not match:
        return default
    return match.group(1).strip()


class MockLlmClient(LlmClient):
    """Cliente determinístico para desarrollo y demos sin proveedor externo."""

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        if "== ETL CONTEXT ==" in user_prompt:
            return self._generate_etl_narrative(user_prompt)
        if "=== PREGUNTA ===" in user_prompt:
            return self._generate_rag_answer(user_prompt)
        return self._generate_summary(system_prompt, user_prompt)

    def _generate_etl_narrative(self, user_prompt: str) -> str:
        strategy = _extract_value(r"^Estrategia:\s*(.+)$", user_prompt, "conservative")
        mode = _extract_value(r"^Modo de ejecución:\s*(.+)$", user_prompt, "manual")
        rows_before = _extract_value(r"Filas:\s*(\d+)\s*→", user_prompt, "N/D")
        rows_after = _extract_value(r"Filas:\s*\d+\s*→\s*(\d+)", user_prompt, "N/D")
        nulls_before = _extract_value(r"Nulos:\s*(\d+)\s*→", user_prompt, "N/D")
        nulls_after = _extract_value(r"Nulos:\s*\d+\s*→\s*(\d+)", user_prompt, "N/D")
        exec_time = _extract_value(r"Tiempo de ejecución:\s*(\d+)ms", user_prompt, "N/D")

        steps = [
            line.strip()[2:].strip()
            for line in user_prompt.splitlines()
            if line.strip().startswith("- [")
        ]
        step_summary = f"Se registraron {len(steps)} paso(s)." if steps else "No se registraron pasos."

        return (
            "## RESUMEN\n"
            f"[Modo demo] Se ejecutó un proceso ETL con estrategia {strategy} "
            f"en modo {mode}. {step_summary}\n\n"
            "## CALIDAD_ORIGINAL\n"
            f"El dataset original contenía {rows_before} filas y {nulls_before} valores nulos, "
            "lo que indicaba la necesidad de un proceso de limpieza.\n\n"
            "## TRANSFORMACIONES\n"
            f"{step_summary} Las transformaciones aplicadas buscaron mejorar "
            "la calidad general del dataset.\n\n"
            "## RESULTADO\n"
            f"Tras la ejecución ({exec_time}ms), el dataset resultante contiene "
            f"{rows_after} filas y {nulls_after} valores nulos.\n\n"
            "## RECOMENDACIONES\n"
            "El proceso ETL se completó satisfactoriamente. Se recomienda revisar "
            "el dataset curado para validar los resultados obtenidos. "
            "Esta narrativa fue generada por el cliente mock para desarrollo local."
        )

    def _generate_summary(self, system_prompt: str, user_prompt: str) -> str:
        dataset_name = _extract_value(r"^Dataset:\s*(.+)$", user_prompt, "dataset")
        rows = _extract_value(r"^Filas:\s*(.+)$", user_prompt, "N/D")
        columns = _extract_value(r"^Columnas:\s*(.+)$", user_prompt, "N/D")
        audience = _extract_value(r"^AUDIENCIA:\s*(.+)$", system_prompt, "equipo técnico")

        insights = [
            line.strip()[2:].strip()
            for line in user_prompt.splitlines()
            if line.strip().startswith("- [")
        ]
        warnings = [
            line.strip()[2:].strip()
            for line in user_prompt.splitlines()
            if line.strip().startswith("-") and "Advertencias:" not in line and "["
            not in line and "(tipo:" not in line
        ]

        lines = [
            f"[Modo demo] Resumen ejecutivo de {dataset_name} para {audience}.",
            f"El dataset contiene {rows} filas y {columns} columnas, con una estructura suficiente para continuar la demostración funcional.",
        ]
        if insights:
            lines.append(f"Hallazgo principal: {insights[0]}")
        if warnings:
            lines.append(f"Advertencia relevante: {warnings[0]}")
        lines.append(
            "Esta respuesta fue generada por el cliente mock configurado para desarrollo local."
        )
        return "\n\n".join(lines)

    def _generate_rag_answer(self, user_prompt: str) -> str:
        question = _extract_value(r"=== PREGUNTA ===\n(.+)$", user_prompt, "Consulta no especificada.")
        dataset_name = _extract_value(r"^Dataset:\s*(.+)$", user_prompt, "dataset")
        source_match = re.search(r"^\[(.+?) #\d+\]$", user_prompt, re.MULTILINE)

        lines = [
            f"[Modo demo] Respuesta para '{question}' usando el contexto disponible de {dataset_name}.",
        ]
        if source_match:
            lines.append(f"Referencia documental utilizada: {source_match.group(1)}.")
        else:
            lines.append("No hay fragmentos documentales indexados; la respuesta se apoya solo en el contexto analítico.")
        lines.append(
            "Esta respuesta fue generada por el cliente mock configurado para desarrollo local."
        )
        return "\n\n".join(lines)
