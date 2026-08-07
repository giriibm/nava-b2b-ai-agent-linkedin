"""Stub OpenAI provider — implement once OPENAI_API_KEY is configured (Phase 2+)."""
from app.config import settings
from app.services.providers.base import LLMProvider


class OpenAIProvider(LLMProvider):
    name = "openai"

    def __init__(self, api_key: str | None = None, model: str = "gpt-4o-mini"):
        self.api_key = api_key or settings.openai_api_key
        self.model = model

    async def generate(self, prompt: str, system: str | None = None, json_mode: bool = False) -> str:
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY not configured")
        import httpx
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        body = {"model": self.model, "messages": messages}
        if json_mode:
            body["response_format"] = {"type": "json_object"}
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json=body,
            )
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]
