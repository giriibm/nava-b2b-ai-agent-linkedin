from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers import icp, prospects, agents, approvals, integrations, jobs
from app.services.llm_gateway import LLMGateway

# MVP: create tables directly. Swap for Alembic migrations before production
# (see backend/README.md).
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Nava AI Outbound Intelligence Platform API",
    description="AI-assisted B2B prospect intelligence — research, scoring, and "
                "personalization behind a mandatory human approval gate.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(icp.router)
app.include_router(prospects.router)
app.include_router(agents.router)
app.include_router(jobs.router)
app.include_router(approvals.router)
app.include_router(integrations.router)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "llm_providers_available": LLMGateway.list_providers(),
    }
