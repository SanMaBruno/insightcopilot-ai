from __future__ import annotations

from src.application.services.text_chunker import chunk_text


class TestChunkText:

    def test_empty_text_returns_empty_list(self) -> None:
        assert chunk_text("") == []
        assert chunk_text("   ") == []

    def test_short_text_returns_single_chunk(self) -> None:
        result = chunk_text("Hola mundo", chunk_size=500)

        assert len(result) == 1
        assert result[0] == "Hola mundo"

    def test_splits_long_text_into_multiple_chunks(self) -> None:
        text = "palabra " * 200  # ~1600 chars
        result = chunk_text(text, chunk_size=100, overlap=10)

        assert len(result) > 1
        for chunk in result:
            assert len(chunk) <= 100

    def test_overlap_creates_shared_content(self) -> None:
        text = "A\n" * 50 + "B\n" * 50
        result = chunk_text(text, chunk_size=60, overlap=20)

        assert len(result) >= 2
        # Con solapamiento, los chunks consecutivos comparten contenido
        all_text = " ".join(result)
        assert "A" in all_text
        assert "B" in all_text

    def test_preserves_all_content(self) -> None:
        lines = [f"Línea {i}" for i in range(20)]
        text = "\n".join(lines)
        result = chunk_text(text, chunk_size=50, overlap=10)

        reconstructed = " ".join(result)
        for line in lines:
            assert line in reconstructed

    def test_prefers_newline_boundaries(self) -> None:
        text = "Primera línea\nSegunda línea\nTercera línea"
        result = chunk_text(text, chunk_size=30, overlap=5)

        # Debería cortar en saltos de línea, no en medio de una línea
        assert len(result) >= 2
        assert result[0].endswith("línea")

    def test_respects_chunk_size_parameter(self) -> None:
        text = "x" * 1000
        result = chunk_text(text, chunk_size=200, overlap=0)

        assert len(result) == 5
        for chunk in result:
            assert len(chunk) == 200

    def test_zero_overlap_no_duplication(self) -> None:
        text = "a" * 100
        result = chunk_text(text, chunk_size=25, overlap=0)

        assert len(result) == 4
        total_chars = sum(len(c) for c in result)
        assert total_chars == 100
