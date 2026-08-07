"""
Lightweight async job runner. Agent calls are long-running AI operations, so
they run in the background (FastAPI BackgroundTasks) with state tracked in the
`jobs` table — the frontend polls GET /api/jobs/{id} rather than blocking on a
synchronous request. Swap this module for a Celery/Redis worker without
changing router code when volume requires it (see Master Spec §12).
"""
import traceback
from typing import Callable, Awaitable

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Job


def create_job(db: Session, job_type: str, entity_type: str, entity_id: str) -> Job:
    job = Job(job_type=job_type, entity_type=entity_type, entity_id=entity_id, status="pending")
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


async def run_job(job_id: str, coro_factory: Callable[[Session], Awaitable[dict]]):
    """Executed in the background. Opens its own DB session since the request's
    session is closed by the time this runs."""
    db = SessionLocal()
    try:
        job = db.query(Job).get(job_id)
        job.status = "running"
        db.commit()

        result = await coro_factory(db)

        job.status = "completed"
        job.result = result
        db.commit()
    except Exception as exc:  # noqa: BLE001 — job runner must never raise into the event loop
        db.rollback()
        job = db.query(Job).get(job_id)
        if job:
            job.status = "failed"
            job.error = f"{exc}\n{traceback.format_exc()[-1000:]}"
            db.commit()
    finally:
        db.close()
