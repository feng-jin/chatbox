"""Build chat/rag prompts with optional history."""
from __future__ import annotations

CHAT_SYSTEM_PREFIX = """你是一个有帮助的对话助手。请结合对话历史回答用户最新问题，回答要简洁准确。"""
RAG_SYSTEM_PREFIX = """你是一个基于文档的问答助手。请根据以下「参考内容」回答用户问题。如果参考内容不足以回答问题，请说明并尽量基于常识回答。回答要简洁准确。"""


def _format_history(history_messages: list[dict] | None) -> str:
    if not history_messages:
        return "(无历史)"
    lines = []
    for m in history_messages:
        role = m.get("role", "")
        content = (m.get("content", "") or "").strip()
        if not content:
            continue
        if role == "assistant":
            lines.append(f"助手: {content}")
        else:
            lines.append(f"用户: {content}")
    return "\n".join(lines) if lines else "(无历史)"


def build_chat_prompt(
    user_message: str,
    history_messages: list[dict] | None = None,
    system_prefix: str | None = None,
) -> str:
    """Build full chat prompt: system + history + latest user message."""
    prefix = system_prefix or CHAT_SYSTEM_PREFIX
    history = _format_history(history_messages)
    return f"{prefix}\n\n【对话历史】\n{history}\n\n【用户最新问题】\n{user_message}"


def build_rag_prompt(
    user_message: str,
    context_chunks: list[str],
    history_messages: list[dict] | None = None,
    system_prefix: str | None = None,
) -> str:
    """Build full RAG prompt: system + history + context + latest user message."""
    prefix = system_prefix or RAG_SYSTEM_PREFIX
    history = _format_history(history_messages)
    context = "\n\n---\n\n".join(context_chunks) if context_chunks else "(无参考内容)"
    return f"{prefix}\n\n【对话历史】\n{history}\n\n【参考内容】\n{context}\n\n【用户最新问题】\n{user_message}"
