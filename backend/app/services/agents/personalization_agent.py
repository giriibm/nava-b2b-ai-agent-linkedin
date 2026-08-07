from sqlalchemy.orm import Session

from app.models import ProspectContact, GeneratedMessage, Channel, MessageStatus, AuditLog
from app.services.llm_gateway import LLMGateway
from app.services.agents import prompts
from app.services.agents.json_utils import parse_json_response


class PersonalizationAgent:
    """Generates LinkedIn/email messaging for human review (Master Spec §4 — Personalization Agent).
    Never sends anything directly — every output is created with status=draft."""

    def __init__(self, gateway: LLMGateway):
        self.gateway = gateway

    async def run(self, db: Session, contact: ProspectContact, channel: str = "linkedin") -> list[GeneratedMessage]:
        company = contact.company
        latest_research = (
            sorted(company.research_records, key=lambda r: r.created_at)[-1]
            if company.research_records else None
        )
        latest_score = (
            sorted(contact.scores, key=lambda s: s.created_at)[-1]
            if contact.scores else None
        )

        prompt = prompts.PERSONALIZATION_PROMPT_TEMPLATE.format(
            full_name=contact.full_name,
            title=contact.title or "unknown title",
            company_name=company.name,
            research_summary=latest_research.summary if latest_research else "not yet researched",
            business_challenges=", ".join(latest_research.business_challenges) if latest_research else "unknown",
            ai_opportunity_areas=", ".join(latest_research.ai_opportunity_areas) if latest_research else "unknown",
            recommended_solution=latest_research.recommended_solution if latest_research else "unknown",
            score=latest_score.score if latest_score else "n/a",
            reasoning=latest_score.reasoning if latest_score else "not yet scored",
        )
        raw = await self.gateway.generate(prompt, system=prompts.PERSONALIZATION_SYSTEM, json_mode=True)
        data = parse_json_response(raw)

        message_map = {
            "connection_request": data.get("connection_request", ""),
            "initial_message": data.get("initial_message", ""),
            "follow_up": data.get("follow_up", ""),
        }

        created: list[GeneratedMessage] = []
        for msg_type, content in message_map.items():
            if not content:
                continue
            msg = GeneratedMessage(
                prospect_contact_id=contact.id,
                channel=Channel.linkedin if channel == "linkedin" else Channel.email,
                message_type=msg_type,
                content=content,
                status=MessageStatus.draft,
            )
            db.add(msg)
            created.append(msg)

        db.add(AuditLog(entity_type="prospect_contact", entity_id=contact.id, action="messages_generated",
                         payload={"channel": channel, "count": len(created), "model": self.gateway.provider.name}))
        db.commit()
        for m in created:
            db.refresh(m)
        return created
