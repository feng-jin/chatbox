"""Text chunking for RAG."""
from __future__ import annotations

from backend.app.core.config import CHUNK_SIZE, CHUNK_OVERLAP


def chunk_text(text: str, chunk_size: int | None = None, overlap: int | None = None) -> list[str]:
    """Split text into overlapping chunks. Defaults from config."""
    size = chunk_size or CHUNK_SIZE
    overlap = overlap if overlap is not None else CHUNK_OVERLAP
    if not text or not text.strip():
        return []
    text = text.strip()
    chunks = []
    start = 0
    while start < len(text):
        end = start + size
        chunk = text[start:end]
        if chunk.strip():
            chunks.append(chunk.strip())
        start = end - overlap
        if start >= len(text):
            break
    return chunks
