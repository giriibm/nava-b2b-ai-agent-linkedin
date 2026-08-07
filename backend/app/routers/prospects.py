from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/api/prospects", tags=["Prospects"])


@router.post("/import", response_model=schemas.ProspectCompanyOut)
def import_prospect(payload: schemas.ProspectCompanyImport, db: Session = Depends(get_db)):
    icp = db.query(models.ICP).get(payload.icp_id)
    if not icp:
        raise HTTPException(404, "ICP not found")

    company = models.ProspectCompany(
        icp_id=payload.icp_id,
        name=payload.name,
        website=payload.website,
        industry=payload.industry,
        location=payload.location,
        employee_count=payload.employee_count,
        source=payload.source,
    )
    db.add(company)
    db.flush()

    for c in payload.contacts:
        db.add(models.ProspectContact(company_id=company.id, **c.model_dump()))

    db.add(models.AuditLog(entity_type="prospect_company", entity_id=company.id, action="imported",
                            payload={"source": payload.source}))
    db.commit()
    db.refresh(company)
    return company


@router.get("", response_model=list[schemas.ProspectCompanyOut])
def list_prospects(
    icp_id: str | None = None,
    stage: str | None = None,
    db: Session = Depends(get_db),
):
    q = db.query(models.ProspectCompany)
    if icp_id:
        q = q.filter(models.ProspectCompany.icp_id == icp_id)
    if stage:
        q = q.filter(models.ProspectCompany.stage == stage)
    return q.order_by(models.ProspectCompany.created_at.desc()).all()


@router.get("/{company_id}", response_model=schemas.ProspectCompanyOut)
def get_prospect(company_id: str, db: Session = Depends(get_db)):
    company = db.query(models.ProspectCompany).get(company_id)
    if not company:
        raise HTTPException(404, "Prospect company not found")
    return company


@router.get("/{company_id}/contacts", response_model=list[schemas.ProspectContactOut])
def list_contacts(company_id: str, db: Session = Depends(get_db)):
    return db.query(models.ProspectContact).filter(models.ProspectContact.company_id == company_id).all()


@router.get("/contacts/{contact_id}", response_model=schemas.ProspectContactDetailOut)
def get_contact(contact_id: str, db: Session = Depends(get_db)):
    contact = db.query(models.ProspectContact).get(contact_id)
    if not contact:
        raise HTTPException(404, "Prospect contact not found")
    return contact
