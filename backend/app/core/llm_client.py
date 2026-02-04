"""LLM client interface and provider implementations."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from backend.app.core.config import LLM_API_KEY, LLM_MODEL, LLM_PROVIDER, LLM_TIMEOUT


@dataclass
class LLMResponse:
    """LLM response with content and optional token usage."""
    content: str
    prompt_tokens: int = 0
    completion_tokens: int = 0


class BaseLLMClient(ABC):
    """Abstract LLM client for dependency injection and testing."""

    @abstractmethod
    def complete(self, prompt: str) -> LLMResponse:
        """Send prompt and return response."""
        pass


class MockLLMClient(BaseLLMClient):
    """Fixed response for tests."""

    def __init__(self, fixed_response: str = "Mock reply.", prompt_tokens: int = 10, completion_tokens: int = 5):
        self.fixed_response = fixed_response
        self.prompt_tokens = prompt_tokens
        self.completion_tokens = completion_tokens

    def complete(self, prompt: str) -> LLMResponse:
        return LLMResponse(
            content=self.fixed_response,
            prompt_tokens=self.prompt_tokens,
            completion_tokens=self.completion_tokens,
        )


def _get_llm_client() -> BaseLLMClient:
    """Return concrete client based on LLM_PROVIDER."""
    if not LLM_API_KEY and LLM_PROVIDER != "mock":
        return MockLLMClient(fixed_response="(未配置 LLM_API_KEY，使用模拟回复)")
    if LLM_PROVIDER.lower() == "mock":
        return MockLLMClient()
    if LLM_PROVIDER.lower() == "gemini":
        from backend.app.core.llm_gemini import GeminiLLMClient
        return GeminiLLMClient()
    if LLM_PROVIDER.lower() == "deepseek":
        from backend.app.core.llm_deepseek import DeepSeekLLMClient
        return DeepSeekLLMClient()
    return MockLLMClient(fixed_response=f"(不支持的 LLM_PROVIDER: {LLM_PROVIDER})")


# Singleton for app use
_default_client: BaseLLMClient | None = None


def get_llm_client() -> BaseLLMClient:
    global _default_client
    if _default_client is None:
        _default_client = _get_llm_client()
    return _default_client


def set_llm_client(client: BaseLLMClient | None) -> None:
    """For tests: inject mock client."""
    global _default_client
    _default_client = client
