from sqlalchemy.orm import Session

from app.models import ProspectCompany, ResearchRecord, ProspectStage, AuditLog
from app.services.llm_gateway import LLMGateway
from app.services.agents import prompts
from app.services.agents.json_utils import parse_json_response


class ResearchAgent:
    """Understands companies and prospects (Master Spec §4 — Research Agent)."""

    def __init__(self, gateway: LLMGateway):
        self.gateway = gateway

    async def run(self, db: Session, company: ProspectCompany) -> ResearchRecord:
        icp = company.icp
        prompt = prompts.RESEARCH_PROMPT_TEMPLATE.format(
            name=company.name,
            website=company.website or "unknown",
            industry=company.industry or (icp.industry if icp else "unknown"),
            location=company.location or (icp.geography if icp else "unknown"),
            employee_count=company.employee_count or "unknown",
            target_roles=", ".join(icp.target_roles) if icp and icp.target_roles else "unknown",
            business_challenges=", ".join(icp.business_challenges) if icp and icp.business_challenges else "unknown",
        )
        raw = await self.gateway.generate(prompt, system=prompts.RESEARCH_SYSTEM, json_mode=True)
        data = parse_json_response(raw)

        record = ResearchRecord(
            prospect_company_id=company.id,
            summary=data.get("summary", ""),
            business_challenges=data.get("business_challenges", []),
            ai_opportunity_areas=data.get("ai_opportunity_areas", []),
            recommended_solution=data.get("recommended_solution", ""),
            model_used=self.gateway.provider.name,
            prompt_version="v1",
        )
        db.add(record)
        company.stage = ProspectStage.researched
        db.add(AuditLog(entity_type="prospect_company", entity_id=company.id, action="research_completed",
                         payload={"model": self.gateway.provider.name}))
        db.commit()
        db.refresh(record)
        return record
