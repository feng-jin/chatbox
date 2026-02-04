"""Build system + context + user prompt for LLM."""
from __future__ import annotations

RAG_SYSTEM_PREFIX = """你是一个基于文档的问答助手。请根据以下「参考内容」回答用户问题。如果参考内容不足以回答问题，请说明并尽量基于常识回答。回答要简洁准确。"""


def build_rag_prompt(
    user_message: str,
    context_chunks: list[str],
    system_prefix: str | None = None,
) -> str:
    """Build full prompt: system + context + user."""
    prefix = system_prefix or RAG_SYSTEM_PREFIX
    context = "\n\n---\n\n".join(context_chunks) if context_chunks else "(无参考内容)"
    return f"{prefix}\n\n【参考内容】\n{context}\n\n【用户问题】\n{user_message}"
