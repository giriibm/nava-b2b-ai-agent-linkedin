"""
Approval & Workflow Service endpoints (Master Spec §5 Step 5, §11).
This router is the ONLY place in the codebase permitted to call HeyReachService.send_message —
enforced architecturally, not just by convention: no AI agent module imports heyreach_service.
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db
from app import models, schemas
from app.services.integrations.heyreach_service import get_heyreach_service

router = APIRouter(prefix="/api/approvals", tags=["Approvals"])


@router.get("/queue", response_model=list[schemas.GeneratedMessageOut])
def get_queue(db: Session = Depends(get_db)):
    return (
        db.query(models.GeneratedMessage)
        .filter(models.GeneratedMessage.status.in_([models.MessageStatus.draft, models.MessageStatus.edited]))
        .order_by(models.GeneratedMessage.created_at.desc())
        .all()
    )


@router.post("/{message_id}/edit", response_model=schemas.GeneratedMessageOut)
def edit_message(message_id: str, payload: schemas.ApprovalDecision, db: Session = Depends(get_db)):
    msg = db.query(models.GeneratedMessage).get(message_id)
    if not msg:
        raise HTTPException(404, "Message not found")
    if not payload.edited_content:
        raise HTTPException(400, "edited_content is required")
    msg.content = payload.edited_content
    msg.status = models.MessageStatus.edited
    db.add(models.AuditLog(entity_type="generated_message", entity_id=message_id, action="edited",
                            actor=payload.reviewer, payload={"reviewer": payload.reviewer}))
    db.commit()
    db.refresh(msg)
    return msg


@router.post("/{message_id}/reject", response_model=schemas.GeneratedMessageOut)
def reject_message(message_id: str, payload: schemas.ApprovalDecision, db: Session = Depends(get_db)):
    msg = db.query(models.GeneratedMessage).get(message_id)
    if not msg:
        raise HTTPException(404, "Message not found")
    msg.status = models.MessageStatus.rejected
    db.add(models.AuditLog(entity_type="generated_message", entity_id=message_id, action="rejected",
                            actor=payload.reviewer, payload={"reason": payload.reason}))
    db.commit()
    db.refresh(msg)
    return msg


@router.post("/{message_id}/approve", response_model=schemas.GeneratedMessageOut)
def approve_message(message_id: str, payload: schemas.ApprovalDecision,
                     background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    msg = db.query(models.GeneratedMessage).get(message_id)
    if not msg:
        raise HTTPException(404, "Message not found")

    msg.status = models.MessageStatus.approved
    msg.approved_by = payload.reviewer
    msg.approved_at = datetime.utcnow()
    db.add(models.AuditLog(entity_type="generated_message", entity_id=message_id, action="approved",
                            actor=payload.reviewer))
    db.commit()
    db.refresh(msg)

    contact = msg.contact
    heyreach = get_heyreach_service()
    if msg.channel == models.Channel.linkedin and heyreach.configured and contact.linkedin_url:
        async def send_task(session):
            from app.models import OutreachActivity, MessageStatus as MS
            svc = get_heyreach_service()
            m = session.query(models.GeneratedMessage).get(message_id)
            await svc.send_message(linkedin_url=m.contact.linkedin_url, message=m.content)
            m.status = MS.sent
            activity = OutreachActivity(generated_message_id=m.id, delivery_channel="heyreach",
                                         sent_at=datetime.utcnow())
            session.add(activity)
            session.add(models.AuditLog(entity_type="generated_message", entity_id=m.id, action="sent_via_heyreach"))
            session.commit()
            return {"sent": True}

        from app.services.job_queue import create_job, run_job
        job = create_job(db, "send_outreach", "generated_message", message_id)
        background_tasks.add_task(run_job, job.id, send_task)
    else:
        db.add(models.AuditLog(entity_type="generated_message", entity_id=message_id,
                                action="approved_awaiting_manual_send",
                                payload={"reason": "HeyReach not configured or missing LinkedIn URL"}))
        db.commit()

    return msg
