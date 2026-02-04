"""Session API tests."""
from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_create_session():
    r = client.post("/api/sessions", json={"title": "API Session"})
    assert r.status_code == 200
    data = r.json()
    assert "session_id" in data
    assert data["title"] == "API Session"


def test_list_sessions():
    r = client.get("/api/sessions")
    assert r.status_code == 200
    data = r.json()
    assert "items" in data
    assert isinstance(data["items"], list)


def test_get_history():
    r = client.post("/api/sessions", json={})
    assert r.status_code == 200
    sid = r.json()["session_id"]
    r2 = client.get(f"/api/history?session_id={sid}")
    assert r2.status_code == 200
    assert "items" in r2.json()
