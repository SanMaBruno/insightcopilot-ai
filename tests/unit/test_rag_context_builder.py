from __future__ import annotations

from src.application.services.rag_context_builder import (
    build_rag_system_prompt,
    build_rag_user_prompt,
)
from src.domain.entities.dataset_insight import DatasetInsightReport, Insight
from src.domain.entities.dataset_profile import DatasetProfile
from src.domain.value_objects.column_profile import ColumnProfile
from src.domain.value_objects.document_chunk import DocumentChunk


class TestBuildRagSystemPrompt:

    def test_includes_no_hallucination_rule(self) -> None:
        result = build_rag_system_prompt()

        assert "ÚNICAMENTE" in result

    def test_includes_source_citation_rule(self) -> None:
        result = build_rag_system_prompt()

        assert "fuente" in result

    def test_includes_spanish_instruction(self) -> None:
        result = build_rag_system_prompt()

        assert "español" in result


class TestBuildRagUserPrompt:

    def _profile(self) -> DatasetProfile:
        return DatasetProfile(
            dataset_id="ds-1",
            row_count=100,
            column_count=2,
            columns=[
                ColumnProfile(name="edad", dtype="int64", null_count=0, unique_count=50),
                ColumnProfile(name="nombre", dtype="object", null_count=0, unique_count=80),
            ],
        )

    def _report(self) -> DatasetInsightReport:
        return DatasetInsightReport(
            dataset_id="ds-1",
            summary="100 filas y 2 columnas",
            insights=[Insight(category="calidad", message="Sin nulos")],
            warnings=[],
        )

    def _chunks(self) -> list[DocumentChunk]:
        return [
            DocumentChunk(source="glosario.md", content="Edad: años del registro", chunk_index=0),
            DocumentChunk(
                source="contexto.txt", content="Datos recopilados en 2024", chunk_index=0,
            ),
        ]

    def test_includes_dataset_name(self) -> None:
        result = build_rag_user_prompt(
            "ventas", self._profile(), self._report(), self._chunks(), "¿Qué hay?",
        )

        assert "ventas" in result

    def test_includes_analytical_context(self) -> None:
        result = build_rag_user_prompt(
            "ventas", self._profile(), self._report(), self._chunks(), "¿Qué hay?",
        )

        assert "100" in result
        assert "edad" in result
        assert "Sin nulos" in result

    def test_includes_document_chunks(self) -> None:
        result = build_rag_user_prompt(
            "ventas", self._profile(), self._report(), self._chunks(), "¿Qué hay?",
        )

        assert "glosario.md" in result
        assert "Edad: años del registro" in result
        assert "contexto.txt" in result

    def test_includes_question(self) -> None:
        result = build_rag_user_prompt(
            "ventas", self._profile(), self._report(),
            self._chunks(), "¿Cuántos registros?",
        )

        assert "¿Cuántos registros?" in result

    def test_omits_document_section_when_no_chunks(self) -> None:
        result = build_rag_user_prompt("ventas", self._profile(), self._report(), [], "pregunta")

        assert "CONTEXTO DOCUMENTAL" not in result

    def test_limits_context_size(self) -> None:
        huge_chunks = [
            DocumentChunk(source=f"doc{i}.txt", content="x" * 3000, chunk_index=0)
            for i in range(5)
        ]

        result = build_rag_user_prompt(
            "ventas", self._profile(), self._report(), huge_chunks, "test",
        )

        # No debería incluir todos los chunks (superarían el límite)
        doc_sections = result.count("CONTEXTO DOCUMENTAL")
        assert doc_sections == 1
        # Verificar que se respeta el límite: el contenido documental no crece sin control
        assert result.count("x" * 3000) < 3
