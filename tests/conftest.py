"""Pytest fixtures: temp DB, mock LLM/embedding."""
import os
import sys
import tempfile
from pathlib import Path

import pytest

# Use temp DB for all tests (before any backend import)
_fd, _temp_db = tempfile.mkstemp(suffix=".db")
os.close(_fd)
os.environ["DATABASE_URL"] = "sqlite:///" + _temp_db

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.app.core.llm_client import MockLLMClient, set_llm_client
from backend.app.core.embeddings import MockEmbedding, set_embedding
from backend.app.db.database import init_db

# Create tables in temp DB once
init_db()


@pytest.fixture(autouse=True)
def mock_llm():
    set_llm_client(MockLLMClient(fixed_response="Test reply.", prompt_tokens=5, completion_tokens=3))
    yield
    set_llm_client(None)


@pytest.fixture(autouse=True)
def mock_embedding():
    set_embedding(MockEmbedding(dim=8))
    yield
    set_embedding(None)


@pytest.fixture
def app_db():
    yield _temp_db
