from __future__ import annotations


def split_text(text: str, chunk_size: int = 800, chunk_overlap: int = 120) -> list[str]:
    """Простой RecursiveCharacter-подобный сплиттер без внешних зависимостей."""
    if not text.strip():
        return []
    separators = ["\n## ", "\n# ", "\n\n", "\n", " ", ""]
    return _split_recursive(text, separators, chunk_size, chunk_overlap)


def _split_recursive(
    text: str, separators: list[str], chunk_size: int, chunk_overlap: int
) -> list[str]:
    if len(text) <= chunk_size:
        return [text] if text.strip() else []

    sep = separators[0] if separators else ""
    rest = separators[1:] if len(separators) > 1 else [""]

    if sep == "":
        chunks = []
        start = 0
        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunks.append(text[start:end])
            if end >= len(text):
                break
            start = max(0, end - chunk_overlap)
        return chunks

    parts = text.split(sep) if sep else [text]
    merged: list[str] = []
    current = ""
    for i, part in enumerate(parts):
        piece = part if i == 0 else sep + part
        if not current:
            current = piece
            continue
        if len(current) + len(piece) <= chunk_size:
            current += piece
        else:
            if len(current) > chunk_size and rest:
                merged.extend(_split_recursive(current, rest, chunk_size, chunk_overlap))
            else:
                merged.append(current)
            current = piece
    if current:
        if len(current) > chunk_size and rest:
            merged.extend(_split_recursive(current, rest, chunk_size, chunk_overlap))
        else:
            merged.append(current)

    # overlap между соседними чанками
    if chunk_overlap <= 0 or len(merged) <= 1:
        return [c for c in merged if c.strip()]

    overlapped: list[str] = []
    for i, chunk in enumerate(merged):
        if i == 0:
            overlapped.append(chunk)
            continue
        prev_tail = merged[i - 1][-chunk_overlap:]
        overlapped.append(prev_tail + chunk)
    return [c for c in overlapped if c.strip()]
