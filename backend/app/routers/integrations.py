from fastapi import APIRouter, HTTPException
from app.services.integrations.salesforce_service import get_salesforce_service
from app.services.integrations.heyreach_service import get_heyreach_service

router = APIRouter(prefix="/api/integrations", tags=["Integrations"])


@router.get("/salesforce/status")
def salesforce_status():
    return get_salesforce_service().health_check()


@router.post("/salesforce/sync")
def salesforce_sync():
    svc = get_salesforce_service()
    if not svc.configured:
        raise HTTPException(501, "Salesforce not configured — set SALESFORCE_* env vars.")
    raise HTTPException(501, "Salesforce sync not yet implemented — see salesforce_service.py TODOs.")


@router.get("/heyreach/status")
def heyreach_status():
    return get_heyreach_service().health_check()
