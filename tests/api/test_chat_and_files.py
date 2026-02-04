"""Chat/files API behavior tests."""
import uuid

from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def test_chat_requires_existing_session():
    missing_session_id = str(uuid.uuid4())
    r = client.post(
        "/api/chat",
        json={"session_id": missing_session_id, "message": "hello"},
    )
    assert r.status_code == 404
    assert r.json()["detail"] == "session not found"


def test_upload_rejects_unsupported_extension():
    r = client.post(
        "/api/files",
        files={"file": ("note.md", b"hello", "text/markdown")},
    )
    assert r.status_code == 400
    assert "Unsupported file type" in r.json()["detail"]


def test_upload_returns_uploaded_when_indexing_fails(monkeypatch):
    def _boom(*args, **kwargs):
        raise RuntimeError("index fail")

    monkeypatch.setattr("backend.app.api.routes_files.rag_service.index_file", _boom)
    r = client.post(
        "/api/files",
        files={"file": ("note.txt", b"hello world", "text/plain")},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "uploaded"
    assert body["indexed"] is False
