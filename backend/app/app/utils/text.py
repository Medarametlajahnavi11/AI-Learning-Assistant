from typing import List


def chunk_text(content: str, chunk_size: int = 1200, overlap: int = 200) -> List[str]:
    chunks: List[str] = []
    start = 0
    length = len(content)

    while start < length:
        end = min(start + chunk_size, length)
        chunks.append(content[start:end].strip())
        if end == length:
            break
        start = max(0, end - overlap)

    return [c for c in chunks if c]
