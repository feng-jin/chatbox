"""Session and history business logic."""
from __future__ import annotations

from backend.app.db import repo


def create_session(title: str = "") -> dict:
    s = repo.create_session(title=title)
    return {"session_id": s["id"], "title": s["title"], "created_at": s["created_at"]}


def list_sessions(limit: int = 50) -> list[dict]:
    rows = repo.list_sessions(limit=limit)
    return [
        {"session_id": r["id"], "title": r["title"], "created_at": r["created_at"], "updated_at": r["updated_at"]}
        for r in rows
    ]


def delete_session(session_id: str) -> bool:
    """Delete session and its messages/files/chunks. Returns True if session existed."""
    return repo.delete_session(session_id)


def get_history(session_id: str, limit: int = 50, before: str | None = None) -> list[dict]:
    rows = repo.list_messages(session_id=session_id, limit=limit, before=before)
    return [
        {"role": r["role"], "content": r["content"], "created_at": r["created_at"]}
        for r in rows
    ]
