"""Gemini API LLM client."""
from __future__ import annotations

import httpx

from backend.app.core.config import LLM_API_KEY, LLM_MODEL, LLM_TIMEOUT
from backend.app.core.llm_client import BaseLLMClient, LLMResponse


class GeminiLLMClient(BaseLLMClient):
    """Google Gemini generateContent client."""

    def __init__(self, api_key: str | None = None, model: str | None = None, timeout: float | None = None):
        self.api_key = api_key or LLM_API_KEY
        self.model = model or LLM_MODEL
        self.timeout = timeout or LLM_TIMEOUT
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"

    def complete(self, prompt: str) -> LLMResponse:
        url = f"{self.base_url}/models/{self.model}:generateContent?key={self.api_key}"
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()

        text = ""
        if data.get("candidates"):
            parts = data["candidates"][0].get("content", {}).get("parts", [])
            text = "".join(p.get("text", "") for p in parts if isinstance(p, dict))

        usage = data.get("usageMetadata", {})
        return LLMResponse(
            content=text,
            prompt_tokens=usage.get("promptTokenCount", 0),
            completion_tokens=usage.get("candidatesTokenCount", 0),
        )
