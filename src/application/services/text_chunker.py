from __future__ import annotations


def chunk_text(
    text: str,
    chunk_size: int = 500,
    overlap: int = 50,
) -> list[str]:
    """Divide texto en fragmentos con solapamiento.

    Corta en el último salto de línea dentro del rango para
    evitar partir oraciones a la mitad cuando sea posible.
    """
    if not text.strip():
        return []

    chunks: list[str] = []
    start = 0
    length = len(text)

    while start < length:
        end = min(start + chunk_size, length)

        if end < length:
            newline_pos = text.rfind("\n", start, end)
            if newline_pos > start:
                end = newline_pos + 1

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        if end >= length:
            break

        start = max(end - overlap, start + 1)

    return chunks
