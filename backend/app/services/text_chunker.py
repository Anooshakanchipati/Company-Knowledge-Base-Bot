def split_text_into_chunks(
    text: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
) -> list[str]:
    if not text.strip():
        return []

    if chunk_size <= 0:
        raise ValueError("Chunk size must be greater than zero")

    if chunk_overlap < 0 or chunk_overlap >= chunk_size:
        raise ValueError(
            "Chunk overlap must be smaller than chunk size"
        )

    chunks = []
    start_position = 0
    text_length = len(text)

    while start_position < text_length:
        end_position = min(
            start_position + chunk_size,
            text_length,
        )

        chunk = text[start_position:end_position].strip()

        if chunk:
            chunks.append(chunk)

        if end_position == text_length:
            break

        start_position = end_position - chunk_overlap

    return chunks