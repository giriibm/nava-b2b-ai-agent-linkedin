import json
import httpx

from app.config import settings
from app.services.providers.base import LLMProvider


class OllamaProvider(LLMProvider):
    """Default provider — talks to a local/self-hosted Ollama instance."""
    name = "ollama"

    def __init__(self, base_url: str | None = None, model: str | None = None):
        self.base_url = base_url or settings.ollama_base_url
        self.model = model or settings.ollama_model

    async def generate(self, prompt: str, system: str | None = None, json_mode: bool = False) -> str:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "system": system or "",
            "stream": False,
        }
        if json_mode:
            payload["format"] = "json"
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                resp = await client.post(f"{self.base_url}/api/generate", json=payload)
                resp.raise_for_status()
                data = resp.json()
                return data.get("response", "")
        except (httpx.ConnectError, httpx.HTTPError) as exc:
            # Ollama not reachable (e.g. not running locally) — fail loudly but
            # predictably so the orchestrator can mark the job failed rather than hang.
            raise RuntimeError(f"Ollama provider unreachable at {self.base_url}: {exc}") from exc
