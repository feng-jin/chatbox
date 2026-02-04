"""RAG: file parse, chunk, embed, index, and retrieve."""
from __future__ import annotations

from backend.app.core.chunker import chunk_text
from backend.app.core.config import RAG_TOP_K, UPLOADS_DIR
from backend.app.core.embeddings import get_embedding, embedding_to_bytes
from backend.app.db import repo
from backend.app.utils.file_parser import parse_file


def index_file(file_id: str, file_path: str) -> None:
    """Parse file, chunk, embed, and store chunks."""
    text = parse_file(file_path)
    chunks = chunk_text(text)
    emb = get_embedding()
    for i, content in enumerate(chunks):
        vec = emb.embed(content)
        blob = embedding_to_bytes(vec)
        repo.add_chunk(file_id=file_id, chunk_index=i, content=content, embedding=blob)


def retrieve(
    query: str,
    file_ids: list[str] | None = None,
    top_k: int | None = None,
) -> list[dict]:
    """Embed query, search chunks, return top_k chunks with content."""
    k = top_k or RAG_TOP_K
    emb = get_embedding()
    query_vec = emb.embed(query)
    rows = repo.search_chunks_by_embedding(file_ids=file_ids, query_embedding=query_vec, top_k=k)
    return [{"file_id": r["file_id"], "chunk_id": r["id"], "content": r["content"]} for r in rows]


def get_context_chunks(query: str, file_ids: list[str] | None = None, top_k: int | None = None) -> list[str]:
    """Return list of chunk content strings for prompt building."""
    hits = retrieve(query=query, file_ids=file_ids, top_k=top_k)
    return [h["content"] for h in hits]
