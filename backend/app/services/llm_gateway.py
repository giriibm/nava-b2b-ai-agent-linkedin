"""
LLM Gateway — the single entry point every AI agent uses to talk to a model.
Provider-agnostic by design (Master Spec §7): swapping LLM_PROVIDER in .env
is the only change needed to move from Ollama to OpenAI/Anthropic/Gemini.
"""
from app.config import settings
from app.services.providers.base import LLMProvider
from app.services.providers.ollama_provider import OllamaProvider
from app.services.providers.openai_provider import OpenAIProvider
from app.services.providers.anthropic_provider import AnthropicProvider
from app.services.providers.gemini_provider import GeminiProvider

_PROVIDERS: dict[str, type[LLMProvider]] = {
    "ollama": OllamaProvider,
    "openai": OpenAIProvider,
    "anthropic": AnthropicProvider,
    "gemini": GeminiProvider,
}


class LLMGateway:
    def __init__(self, provider_name: str | None = None):
        provider_name = (provider_name or settings.llm_provider).lower()
        provider_cls = _PROVIDERS.get(provider_name)
        if not provider_cls:
            raise ValueError(f"Unknown LLM provider '{provider_name}'. Available: {list(_PROVIDERS)}")
        self.provider: LLMProvider = provider_cls()

    async def generate(self, prompt: str, system: str | None = None, json_mode: bool = False) -> str:
        return await self.provider.generate(prompt, system=system, json_mode=json_mode)

    @staticmethod
    def list_providers() -> list[str]:
        return list(_PROVIDERS.keys())


def get_llm_gateway() -> LLMGateway:
    return LLMGateway()
