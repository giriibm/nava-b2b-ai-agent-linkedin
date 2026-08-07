"""
HeyReach Integration Service (Master Spec §4, §11).

This is the ONLY module in the platform permitted to trigger outbound
LinkedIn delivery, and it is only ever called by the Approval & Workflow
Service after a human has approved a GeneratedMessage — no AI agent may call
this directly. Delivery is throttled to reflect authentic, human-paced
sales activity, not bulk sending.
"""
import httpx

from app.config import settings


class HeyReachService:
    def __init__(self):
        self.configured = bool(settings.heyreach_api_key)
        self.base_url = settings.heyreach_base_url

    async def send_message(self, linkedin_url: str, message: str, campaign_id: str | None = None) -> dict:
        if not self.configured:
            raise RuntimeError("HeyReach is not configured. Set HEYREACH_API_KEY in .env.")
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                f"{self.base_url}/campaigns/AddLeadToCampaign",
                headers={"X-API-KEY": settings.heyreach_api_key},
                json={"linkedInUrl": linkedin_url, "message": message, "campaignId": campaign_id},
            )
            resp.raise_for_status()
            return resp.json()

    def health_check(self) -> dict:
        return {"configured": self.configured}


def get_heyreach_service() -> HeyReachService:
    return HeyReachService()
