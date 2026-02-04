"""Chat API."""
from fastapi import APIRouter, HTTPException

from backend.app.services import chat_service

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat")
def chat(body: dict):
    session_id = body.get("session_id")
    message = body.get("message", "").strip()
    if not session_id or not message:
        raise HTTPException(status_code=400, detail="session_id and message are required")
    use_rag = body.get("use_rag", False)
    file_ids = body.get("file_ids") or []
    try:
        out = chat_service.chat(session_id=session_id, message=message, use_rag=use_rag, file_ids=file_ids)
    except ValueError as e:
        if str(e) == "session not found":
            raise HTTPException(status_code=404, detail="session not found")
        raise HTTPException(status_code=400, detail=str(e))
    return {
        "assistant_message": out["assistant_message"],
        "citations": out["citations"],
        "token_usage": out["token_usage"],
    }
