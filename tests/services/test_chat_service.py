"""Chat service tests (mock LLM)."""
import pytest
from backend.app.core.llm_client import BaseLLMClient, LLMResponse, set_llm_client
from backend.app.services import chat_service
from backend.app.services import session_service


@pytest.fixture
def db(app_db):
    return app_db


class CaptureLLMClient(BaseLLMClient):
    def __init__(self):
        self.prompts = []

    def complete(self, prompt: str) -> LLMResponse:
        self.prompts.append(prompt)
        return LLMResponse(content="Captured reply.", prompt_tokens=1, completion_tokens=1)


def test_chat_no_rag(db):
    s = session_service.create_session(title="Chat")
    out = chat_service.chat(session_id=s["session_id"], message="Hello", use_rag=False)
    assert "assistant_message" in out
    assert out["assistant_message"] == "Test reply."
    assert out["token_usage"]["prompt"] == 5 and out["token_usage"]["completion"] == 3
    assert out["citations"] == []


def test_chat_with_rag_empty_files(db):
    s = session_service.create_session(title="RAG")
    out = chat_service.chat(session_id=s["session_id"], message="Hi", use_rag=True, file_ids=[])
    assert "assistant_message" in out
    assert out["citations"] == []


def test_chat_prompt_includes_recent_history(db):
    cap = CaptureLLMClient()
    set_llm_client(cap)

    s = session_service.create_session(title="History")
    chat_service.chat(session_id=s["session_id"], message="第一问", use_rag=False)
    chat_service.chat(session_id=s["session_id"], message="第二问", use_rag=False)

    latest_prompt = cap.prompts[-1]
    assert "【对话历史】" in latest_prompt
    assert "用户: 第一问" in latest_prompt
    assert "助手: Captured reply." in latest_prompt
    assert "【用户最新问题】\n第二问" in latest_prompt
