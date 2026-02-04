"""Embedding interface and implementations for RAG."""
from __future__ import annotations

from abc import ABC, abstractmethod
import struct
import httpx
from backend.app.core.config import (
    EMBEDDING_DIM,
    EMBEDDING_MODEL,
    EMBEDDING_PROVIDER,
    LLM_API_KEY,
    LLM_TIMEOUT,
)


def embedding_to_bytes(vec: list[float]) -> bytes:
    """Store embedding as float32 bytes for SQLite BLOB."""
    return struct.pack(f"{len(vec)}f", *vec)


def bytes_to_embedding(b: bytes) -> list[float]:
    """Load embedding from BLOB."""
    n = len(b) // 4
    return list(struct.unpack(f"{n}f", b))


class BaseEmbedding(ABC):
    @abstractmethod
    def embed(self, text: str) -> list[float]:
        pass

    @abstractmethod
    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        pass


class MockEmbedding(BaseEmbedding):
    """Deterministic fake embedding for tests."""

    def __init__(self, dim: int = 8):
        self.dim = dim

    def embed(self, text: str) -> list[float]:
        # Deterministic from hash of text
        h = hash(text) % (2 ** 31)
        return [float((h + i) % 100) / 100.0 for i in range(self.dim)]

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        return [self.embed(t) for t in texts]


class GeminiEmbedding(BaseEmbedding):
    """Gemini embedding API (text-embedding-004)."""

    def __init__(self, api_key: str | None = None, model: str | None = None, timeout: float | None = None):
        self.api_key = api_key or LLM_API_KEY
        self.model = model or EMBEDDING_MODEL
        self.timeout = timeout or LLM_TIMEOUT
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"

    def embed(self, text: str) -> list[float]:
        return self.embed_batch([text])[0]

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        url = f"{self.base_url}/models/{self.model}:embedContent?key={self.api_key}"
        results = []
        for text in texts:
            payload = {"model": f"models/{self.model}", "content": {"parts": [{"text": text}]}}
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.post(url, json=payload)
                resp.raise_for_status()
                data = resp.json()
            vec = data.get("embedding", {}).get("values", [])
            results.append([float(x) for x in vec])
        return results


_default_embedding: BaseEmbedding | None = None


def get_embedding() -> BaseEmbedding:
    global _default_embedding
    if _default_embedding is None:
        if not LLM_API_KEY or EMBEDDING_PROVIDER.lower() in ("mock", ""):
            _default_embedding = MockEmbedding(dim=EMBEDDING_DIM)
        elif EMBEDDING_PROVIDER.lower() == "gemini":
            _default_embedding = GeminiEmbedding()
        else:
            _default_embedding = MockEmbedding(dim=EMBEDDING_DIM)
    return _default_embedding


def set_embedding(emb: BaseEmbedding | None) -> None:
    global _default_embedding
    _default_embedding = emb
