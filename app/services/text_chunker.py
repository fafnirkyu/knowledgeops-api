from dataclasses import dataclass


@dataclass(frozen=True)
class TextChunk:
    chunk_index: int
    content: str
    start_offset: int
    end_offset: int

def chunk_text(
    text: str,
    *,
    chunk_size: int = 1000,
    overlap: int = 200,
    ) -> list[TextChunk]:
        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than zero")

        if overlap < 0:
            raise ValueError("overlap cannot be negative")

        if overlap >= chunk_size:
            raise ValueError("overlap must be smaller than chunk_size")

        if not text:
            return []

        chunks: list[TextChunk] = []
        start_offset = 0
        chunk_index = 0
        while start_offset < len(text):
            end_offset = min(
                start_offset + chunk_size,
                len(text),
            )

            chunks.append(
                TextChunk(
                    chunk_index=chunk_index,
                    content=text[start_offset:end_offset],
                    start_offset=start_offset,
                    end_offset=end_offset,
                )
            )

            if end_offset == len(text):
                break

            start_offset = end_offset - overlap
            chunk_index += 1

        return chunks