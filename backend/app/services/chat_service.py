"""Chat flow: save message, optional RAG, LLM, save reply."""
from __future__ import annotations

from backend.app.core.llm_client import get_llm_client
from backend.app.core.prompt_builder import build_chat_prompt, build_rag_prompt
from backend.app.db import repo
from backend.app.services import rag_service


def chat(
    session_id: str,
    message: str,
    use_rag: bool = False,
    file_ids: list[str] | None = None,
) -> dict:
    """Save user message, optionally retrieve context, call LLM, save assistant message, return reply."""
    if not repo.get_session(session_id):
        raise ValueError("session not found")

    # Read recent history before writing latest user message, so prompt is not duplicated.
    history = repo.list_messages(session_id=session_id, limit=20)
    # If this is the first message, use it as the session title for the list.
    if not history:
        repo.update_session_title(session_id, message)
    repo.add_message(session_id=session_id, role="user", content=message)
    if use_rag and file_ids:
        context_chunks = rag_service.get_context_chunks(query=message, file_ids=file_ids)
        prompt = build_rag_prompt(
            user_message=message,
            context_chunks=context_chunks,
            history_messages=history,
        )
    else:
        prompt = build_chat_prompt(user_message=message, history_messages=history)
    client = get_llm_client()
    resp = client.complete(prompt)
    repo.add_message(session_id=session_id, role="assistant", content=resp.content)
    citations = []
    if use_rag and file_ids:
        hits = rag_service.retrieve(query=message, file_ids=file_ids, top_k=5)
        citations = [{"file_id": h["file_id"], "chunk_id": h["chunk_id"]} for h in hits]
    return {
        "assistant_message": resp.content,
        "citations": citations,
        "token_usage": {"prompt": resp.prompt_tokens, "completion": resp.completion_tokens},
    }
