"""
AI Agent Orchestrator (Master Spec §8): coordinates Research -> Scoring ->
Personalization in sequence, and is the only thing the routers call — routers
never talk to an individual agent or the LLM Gateway directly.
"""
from sqlalchemy.orm import Session

from app.models import ProspectCompany, ProspectContact
from app.services.llm_gateway import LLMGateway
from app.services.agents.research_agent import ResearchAgent
from app.services.agents.scoring_agent import ScoringAgent
from app.services.agents.personalization_agent import PersonalizationAgent


class AgentOrchestrator:
    def __init__(self, gateway: LLMGateway | None = None):
        self.gateway = gateway or LLMGateway()
        self.research_agent = ResearchAgent(self.gateway)
        self.scoring_agent = ScoringAgent(self.gateway)
        self.personalization_agent = PersonalizationAgent(self.gateway)

    async def run_research(self, db: Session, company: ProspectCompany):
        return await self.research_agent.run(db, company)

    async def run_scoring(self, db: Session, contact: ProspectContact):
        return await self.scoring_agent.run(db, contact)

    async def run_personalization(self, db: Session, contact: ProspectContact, channel: str = "linkedin"):
        return await self.personalization_agent.run(db, contact, channel=channel)
