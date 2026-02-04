"""DeepSeek API LLM client."""
from __future__ import annotations

import httpx
from backend.app.core.config import LLM_API_KEY, LLM_MODEL, LLM_TIMEOUT
from backend.app.core.llm_client import BaseLLMClient, LLMResponse


class DeepSeekLLMClient(BaseLLMClient):
    """DeepSeek API completion client."""

    def __init__(self, api_key: str | None = None, model: str | None = None, timeout: float | None = None):
        self.api_key = api_key or LLM_API_KEY
        self.model = model or LLM_MODEL
        self.timeout = timeout or LLM_TIMEOUT
        self.base_url = "https://api.deepseek.com/v1"

    def complete(self, prompt: str) -> LLMResponse:
        url = f"{self.base_url}/chat/completions"
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 2048,
        }
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
        text = ""
        usage = {"prompt_tokens": 0, "completion_tokens": 0}
        if "choices" in data and data["choices"]:
            text = data["choices"][0].get("message", {}).get("content", "")
        if "usage" in data:
            usage = {
                "prompt_tokens": data["usage"].get("prompt_tokens", 0),
                "completion_tokens": data["usage"].get("completion_tokens", 0),
            }
        return LLMResponse(
            content=text,
            prompt_tokens=usage.get("prompt_tokens", 0),
            completion_tokens=usage.get("completion_tokens", 0),
        )
