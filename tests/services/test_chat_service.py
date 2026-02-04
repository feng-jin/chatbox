"""Chat service tests (mock LLM)."""
import pytest
from backend.app.services import chat_service
from backend.app.services import session_service


@pytest.fixture
def db(app_db):
    return app_db


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
