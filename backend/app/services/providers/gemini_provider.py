"""Stub Google Gemini provider — implement once GEMINI_API_KEY is configured (Phase 2+)."""
from app.config import settings
from app.services.providers.base import LLMProvider


class GeminiProvider(LLMProvider):
    name = "gemini"

    def __init__(self, api_key: str | None = None, model: str = "gemini-1.5-flash"):
        self.api_key = api_key or settings.gemini_api_key
        self.model = model

    async def generate(self, prompt: str, system: str | None = None, json_mode: bool = False) -> str:
        if not self.api_key:
            raise RuntimeError("GEMINI_API_KEY not configured")
        import httpx
        full_prompt = f"{system}\n\n{prompt}" if system else prompt
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        body = {"contents": [{"parts": [{"text": full_prompt}]}]}
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(url, json=body)
            resp.raise_for_status()
            data = resp.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]
