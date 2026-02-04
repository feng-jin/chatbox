"""Chunker tests."""
import pytest
from backend.app.core.chunker import chunk_text


def test_chunk_empty():
    assert chunk_text("") == []
    assert chunk_text("   ") == []


def test_chunk_short():
    text = "Hello world."
    chunks = chunk_text(text, chunk_size=100, overlap=10)
    assert len(chunks) == 1
    assert chunks[0] == "Hello world."


def test_chunk_splits():
    text = "a" * 500 + " b " + "c" * 500
    chunks = chunk_text(text, chunk_size=200, overlap=20)
    assert len(chunks) >= 2
    joined = "".join(chunks)
    assert "b" in joined
    assert joined.count("a") >= 500
    assert joined.count("c") >= 500


def test_chunk_overlap_behavior():
    text = "x" * 450
    chunks = chunk_text(text, chunk_size=200, overlap=20)
    assert len(chunks) == 3
    assert chunks[0][-20:] == chunks[1][:20]
    assert chunks[1][-20:] == chunks[2][:20]
