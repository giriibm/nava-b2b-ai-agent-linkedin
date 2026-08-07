"""
Salesforce Integration Service (Master Spec §6, §11).

Salesforce is the system of record — this service only pushes prospect
intelligence references (Account/Lead/Contact/Task IDs) into Salesforce and
never duplicates pipeline data locally. Uses the standard username-password +
security-token OAuth flow. Swap the HTTP calls below for `simple-salesforce`
once real credentials are available; the public methods are the stable
contract routers depend on.
"""
from app.config import settings


class SalesforceService:
    def __init__(self):
        self.configured = bool(settings.salesforce_client_id and settings.salesforce_username)

    def _require_configured(self):
        if not self.configured:
            raise RuntimeError(
                "Salesforce is not configured. Set SALESFORCE_CLIENT_ID / "
                "SALESFORCE_USERNAME / SALESFORCE_PASSWORD in .env."
            )

    def upsert_account(self, company: dict) -> str:
        """Create/update a Salesforce Account for a prospect company. Returns the Account Id."""
        self._require_configured()
        # TODO(Phase 1 rollout): call Salesforce REST API `/sobjects/Account`
        raise NotImplementedError("Wire up real Salesforce REST/Bulk API calls here.")

    def upsert_lead(self, contact: dict) -> str:
        """Create/update a Salesforce Lead for a prospect contact. Returns the Lead Id."""
        self._require_configured()
        raise NotImplementedError("Wire up real Salesforce REST/Bulk API calls here.")

    def create_task(self, contact_salesforce_id: str, subject: str, notes: str) -> str:
        """Log a follow-up Task tied to a Lead/Contact. Returns the Task Id."""
        self._require_configured()
        raise NotImplementedError("Wire up real Salesforce REST/Bulk API calls here.")

    def health_check(self) -> dict:
        return {"configured": self.configured, "domain": settings.salesforce_domain}


def get_salesforce_service() -> SalesforceService:
    return SalesforceService()
