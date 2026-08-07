"""Stub Anthropic provider — implement once ANTHROPIC_API_KEY is configured (Phase 2+)."""
from app.config import settings
from app.services.providers.base import LLMProvider


class AnthropicProvider(LLMProvider):
    name = "anthropic"

    def __init__(self, api_key: str | None = None, model: str = "claude-sonnet-5"):
        self.api_key = api_key or settings.anthropic_api_key
        self.model = model

    async def generate(self, prompt: str, system: str | None = None, json_mode: bool = False) -> str:
        if not self.api_key:
            raise RuntimeError("ANTHROPIC_API_KEY not configured")
        import httpx
        body = {
            "model": self.model,
            "max_tokens": 2048,
            "system": system or "",
            "messages": [{"role": "user", "content": prompt}],
        }
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json=body,
            )
            resp.raise_for_status()
            data = resp.json()
            return "".join(block.get("text", "") for block in data.get("content", []))
