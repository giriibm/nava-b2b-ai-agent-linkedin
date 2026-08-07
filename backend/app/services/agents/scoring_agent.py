from sqlalchemy.orm import Session

from app.models import ProspectContact, ScoreRecord, ProspectStage, AuditLog
from app.services.llm_gateway import LLMGateway
from app.services.agents import prompts
from app.services.agents.json_utils import parse_json_response


class ScoringAgent:
    """Prioritizes best prospects with a 0-100 AI Fit Score (Master Spec §4 — Scoring Agent)."""

    def __init__(self, gateway: LLMGateway):
        self.gateway = gateway

    async def run(self, db: Session, contact: ProspectContact) -> ScoreRecord:
        company = contact.company
        latest_research = (
            sorted(company.research_records, key=lambda r: r.created_at)[-1]
            if company.research_records else None
        )
        icp = company.icp

        prompt = prompts.SCORING_PROMPT_TEMPLATE.format(
            full_name=contact.full_name,
            title=contact.title or "unknown title",
            company_name=company.name,
            industry=company.industry or "unknown",
            employee_count=company.employee_count or "unknown",
            location=company.location or "unknown",
            research_summary=latest_research.summary if latest_research else "not yet researched",
            business_challenges=", ".join(latest_research.business_challenges) if latest_research else "unknown",
            ai_opportunity_areas=", ".join(latest_research.ai_opportunity_areas) if latest_research else "unknown",
            target_roles=", ".join(icp.target_roles) if icp and icp.target_roles else "unknown",
        )
        raw = await self.gateway.generate(prompt, system=prompts.SCORING_SYSTEM, json_mode=True)
        data = parse_json_response(raw)
        score = max(0, min(100, int(data.get("score", 0))))

        record = ScoreRecord(
            prospect_contact_id=contact.id,
            score=score,
            reasoning=data.get("reasoning", ""),
            factors=data.get("factors", {}),
            model_used=self.gateway.provider.name,
        )
        db.add(record)
        company.stage = ProspectStage.scored
        db.add(AuditLog(entity_type="prospect_contact", entity_id=contact.id, action="scored",
                         payload={"score": score, "model": self.gateway.provider.name}))
        db.commit()
        db.refresh(record)
        return record
