"""CRUD and queries for sessions, messages, files, chunks."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from backend.app.db.database import get_connection


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# Sessions
def create_session(title: str = "") -> dict:
    sid = str(uuid.uuid4())
    now = _now_iso()
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO sessions (id, title, created_at, updated_at) VALUES (?, ?, ?, ?)",
            (sid, title or "", now, now),
        )
    return {"id": sid, "title": title or "", "created_at": now, "updated_at": now}


def list_sessions(limit: int = 50) -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, title, created_at, updated_at FROM sessions ORDER BY updated_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return [dict(r) for r in rows]


def get_session(session_id: str) -> Optional[dict]:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT id, title, created_at, updated_at FROM sessions WHERE id = ?",
            (session_id,),
        ).fetchone()
    return dict(row) if row else None


def touch_session(session_id: str) -> None:
    now = _now_iso()
    with get_connection() as conn:
        conn.execute("UPDATE sessions SET updated_at = ? WHERE id = ?", (now, session_id))


def delete_session(session_id: str) -> bool:
    """Delete session and its messages, files, chunks. Returns True if session existed."""
    if not get_session(session_id):
        return False
    with get_connection() as conn:
        conn.execute("DELETE FROM chunks WHERE file_id IN (SELECT id FROM files WHERE session_id = ?)", (session_id,))
        conn.execute("DELETE FROM files WHERE session_id = ?", (session_id,))
        conn.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
        conn.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
    return True


# Messages
def add_message(session_id: str, role: str, content: str) -> dict:
    mid = str(uuid.uuid4())
    now = _now_iso()
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO messages (id, session_id, role, content, created_at) VALUES (?, ?, ?, ?, ?)",
            (mid, session_id, role, content, now),
        )
    touch_session(session_id)
    return {"id": mid, "session_id": session_id, "role": role, "content": content, "created_at": now}


def list_messages(
    session_id: str,
    limit: int = 50,
    before: Optional[str] = None,
) -> list:
    with get_connection() as conn:
        if before:
            rows = conn.execute(
                """SELECT id, session_id, role, content, created_at FROM messages
                   WHERE session_id = ? AND created_at < ? ORDER BY created_at DESC LIMIT ?""",
                (session_id, before, limit),
            ).fetchall()
        else:
            rows = conn.execute(
                """SELECT id, session_id, role, content, created_at FROM messages
                   WHERE session_id = ? ORDER BY created_at DESC LIMIT ?""",
                (session_id, limit),
            ).fetchall()
    return [dict(r) for r in reversed(rows)]


# Files
def create_file(
    filename: str,
    path: str,
    mime_type: Optional[str] = None,
    session_id: Optional[str] = None,
) -> dict:
    fid = str(uuid.uuid4())
    now = _now_iso()
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO files (id, session_id, filename, mime_type, path, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (fid, session_id, filename, mime_type or "", path, now),
        )
    return {"id": fid, "session_id": session_id, "filename": filename, "mime_type": mime_type or "", "path": path, "created_at": now}


def get_file(file_id: str) -> Optional[dict]:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT id, session_id, filename, mime_type, path, created_at FROM files WHERE id = ?",
            (file_id,),
        ).fetchone()
    return dict(row) if row else None


# Chunks
def add_chunk(file_id: str, chunk_index: int, content: str, embedding: Optional[bytes] = None) -> dict:
    cid = str(uuid.uuid4())
    now = _now_iso()
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO chunks (id, file_id, chunk_index, content, embedding, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (cid, file_id, chunk_index, content, embedding, now),
        )
    return {"id": cid, "file_id": file_id, "chunk_index": chunk_index, "content": content, "created_at": now}


def list_chunks_by_file(file_id: str) -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, file_id, chunk_index, content, created_at FROM chunks WHERE file_id = ? ORDER BY chunk_index",
            (file_id,),
        ).fetchall()
    return [dict(r) for r in rows]


def search_chunks_by_embedding(file_ids: Optional[list], query_embedding: list, top_k: int) -> list[dict]:
    """Return chunks with embedding stored; similarity done in Python (cosine). file_ids=None means all files."""
    with get_connection() as conn:
        if file_ids:
            placeholders = ",".join("?" * len(file_ids))
            rows = conn.execute(
                f"SELECT id, file_id, chunk_index, content, embedding FROM chunks WHERE file_id IN ({placeholders})",
                file_ids,
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT id, file_id, chunk_index, content, embedding FROM chunks",
            ).fetchall()
    # Cosine similarity in Python (simple; for production use faiss/sqlite-vec)
    import math
    results = []
    for r in rows:
        emb = r["embedding"]
        if emb is None:
            continue
        # Assume embedding stored as bytes of float32 array
        try:
            import struct
            vec = list(struct.unpack(f"{len(emb)//4}f", emb))
        except Exception:
            continue
        dot = sum(a * b for a, b in zip(query_embedding, vec))
        norm_q = math.sqrt(sum(x * x for x in query_embedding)) or 1e-9
        norm_v = math.sqrt(sum(x * x for x in vec)) or 1e-9
        score = dot / (norm_q * norm_v)
        results.append((score, dict(r)))
    results.sort(key=lambda x: -x[0])
    return [r[1] for r in results[:top_k]]
