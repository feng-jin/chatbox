"""Session service tests."""
import pytest
from backend.app.db import repo
from backend.app.db.database import get_connection
from backend.app.services import session_service


@pytest.fixture
def db(app_db):
    return app_db


def test_create_session(db):
    out = session_service.create_session(title="Test")
    assert "session_id" in out
    assert out["title"] == "Test"
    assert "created_at" in out


def test_list_sessions(db):
    session_service.create_session(title="A")
    session_service.create_session(title="B")
    items = session_service.list_sessions(limit=10)
    assert len(items) >= 2
    titles = [s["title"] for s in items]
    assert "A" in titles and "B" in titles


def test_get_history_empty(db):
    s = session_service.create_session(title="H")
    items = session_service.get_history(session_id=s["session_id"])
    assert items == []


def test_get_history_after_messages(db):
    s = session_service.create_session(title="H")
    repo.add_message(session_id=s["session_id"], role="user", content="hi")
    repo.add_message(session_id=s["session_id"], role="assistant", content="hello")
    items = session_service.get_history(session_id=s["session_id"])
    assert len(items) == 2
    assert items[0]["role"] == "user" and items[0]["content"] == "hi"
    assert items[1]["role"] == "assistant" and items[1]["content"] == "hello"
