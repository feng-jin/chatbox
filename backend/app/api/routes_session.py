"""Session and history API."""
from __future__ import annotations

from fastapi import APIRouter, Body

from backend.app.services import session_service

router = APIRouter(prefix="/api", tags=["sessions"])


@router.post("/sessions")
def create_session(body: dict | None = Body(None)):
    title = (body or {}).get("title", "")
    out = session_service.create_session(title=title)
    return {"session_id": out["session_id"], "title": out["title"], "created_at": out["created_at"]}


@router.get("/sessions")
def list_sessions():
    items = session_service.list_sessions()
    return {"items": [{"session_id": s["session_id"], "title": s["title"], "updated_at": s["updated_at"]} for s in items]}


@router.get("/history")
def get_history(session_id: str, limit: int = 50, before: str | None = None):
    items = session_service.get_history(session_id=session_id, limit=limit, before=before)
    return {"items": [{"role": i["role"], "content": i["content"], "created_at": i["created_at"]} for i in items]}
