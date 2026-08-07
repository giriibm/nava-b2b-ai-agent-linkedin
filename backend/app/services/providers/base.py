"""
Provider interface that every LLM backend must implement.
This is the abstraction referenced in Master Spec §7/§8 — the application
talks to `LLMProvider`, never to a vendor SDK directly, so providers can be
swapped (Ollama -> OpenAI -> Anthropic -> Gemini) without touching agent code.
"""
from abc import ABC, abstractmethod


class LLMProvider(ABC):
    name: str = "base"

    @abstractmethod
    async def generate(self, prompt: str, system: str | None = None, json_mode: bool = False) -> str:
        """Return raw text (or JSON string, if json_mode=True) completion for a prompt."""
        raise NotImplementedError
