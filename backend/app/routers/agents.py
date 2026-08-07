"""
Endpoints that trigger AI agent jobs. Every trigger is async: it creates a
Job row and schedules the work in the background, returning immediately with
a job_id the frontend polls via GET /api/jobs/{id} (Master Spec §10, §12).
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from app.database import get_db
from app import models
from app.services.job_queue import create_job, run_job
from app.services.agents.orchestrator import AgentOrchestrator

router = APIRouter(prefix="/api/prospects", tags=["AI Agents"])


@router.post("/{company_id}/research")
def trigger_research(company_id: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    company = db.query(models.ProspectCompany).get(company_id)
    if not company:
        raise HTTPException(404, "Prospect company not found")

    job = create_job(db, "research", "prospect_company", company_id)

    async def task(session):
        orchestrator = AgentOrchestrator()
        co = session.query(models.ProspectCompany).get(company_id)
        record = await orchestrator.run_research(session, co)
        return {"research_record_id": record.id, "summary": record.summary}

    background_tasks.add_task(run_job, job.id, task)
    return {"job_id": job.id, "status": "pending"}


@router.post("/contacts/{contact_id}/score")
def trigger_scoring(contact_id: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    contact = db.query(models.ProspectContact).get(contact_id)
    if not contact:
        raise HTTPException(404, "Prospect contact not found")

    job = create_job(db, "score", "prospect_contact", contact_id)

    async def task(session):
        orchestrator = AgentOrchestrator()
        ct = session.query(models.ProspectContact).get(contact_id)
        record = await orchestrator.run_scoring(session, ct)
        return {"score_record_id": record.id, "score": record.score}

    background_tasks.add_task(run_job, job.id, task)
    return {"job_id": job.id, "status": "pending"}


@router.post("/contacts/{contact_id}/generate-message")
def trigger_personalization(
    contact_id: str,
    background_tasks: BackgroundTasks,
    channel: str = "linkedin",
    db: Session = Depends(get_db),
):
    contact = db.query(models.ProspectContact).get(contact_id)
    if not contact:
        raise HTTPException(404, "Prospect contact not found")

    job = create_job(db, "generate_message", "prospect_contact", contact_id)

    async def task(session):
        orchestrator = AgentOrchestrator()
        ct = session.query(models.ProspectContact).get(contact_id)
        messages = await orchestrator.run_personalization(session, ct, channel=channel)
        return {"message_ids": [m.id for m in messages]}

    background_tasks.add_task(run_job, job.id, task)
    return {"job_id": job.id, "status": "pending"}
