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
        if "=== PREGUNTA ===" in user_prompt:
            return self._generate_rag_answer(user_prompt)
        return self._generate_summary(system_prompt, user_prompt)

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
