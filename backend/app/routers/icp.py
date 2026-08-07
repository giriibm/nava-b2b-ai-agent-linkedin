from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/api/icp", tags=["ICP"])


@router.post("", response_model=schemas.ICPOut)
def create_icp(payload: schemas.ICPCreate, db: Session = Depends(get_db)):
    org = db.query(models.Organization).get(payload.organization_id)
    if not org:
        org = models.Organization(id=payload.organization_id, name=payload.organization_id)
        db.add(org)
        db.commit()
    icp = models.ICP(**payload.model_dump())
    db.add(icp)
    db.commit()
    db.refresh(icp)
    return icp


@router.get("", response_model=list[schemas.ICPOut])
def list_icps(db: Session = Depends(get_db)):
    return db.query(models.ICP).order_by(models.ICP.created_at.desc()).all()


@router.get("/{icp_id}", response_model=schemas.ICPOut)
def get_icp(icp_id: str, db: Session = Depends(get_db)):
    icp = db.query(models.ICP).get(icp_id)
    if not icp:
        raise HTTPException(404, "ICP not found")
    return icp
