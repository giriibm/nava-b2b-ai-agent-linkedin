"""Pydantic request/response schemas for the API layer (see Master Spec §10)."""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict


class ICPCreate(BaseModel):
    organization_id: str
    name: str
    industry: Optional[str] = None
    geography: Optional[str] = None
    company_size_range: Optional[str] = None
    revenue_range: Optional[str] = None
    target_roles: List[str] = []
    keywords: List[str] = []
    business_challenges: List[str] = []


class ICPOut(ICPCreate):
    model_config = ConfigDict(from_attributes=True)
    id: str
    created_at: datetime


class ProspectContactIn(BaseModel):
    full_name: str
    title: Optional[str] = None
    linkedin_url: Optional[str] = None
    email: Optional[str] = None


class ProspectCompanyImport(BaseModel):
    icp_id: str
    name: str
    website: Optional[str] = None
    industry: Optional[str] = None
    location: Optional[str] = None
    employee_count: Optional[int] = None
    source: str = "linkedin_sales_navigator_export"
    contacts: List[ProspectContactIn] = []


class ProspectContactOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    company_id: str
    full_name: str
    title: Optional[str] = None
    linkedin_url: Optional[str] = None
    email: Optional[str] = None


class ResearchRecordOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())
    id: str
    summary: Optional[str] = None
    business_challenges: List[str] = []
    ai_opportunity_areas: List[str] = []
    recommended_solution: Optional[str] = None
    model_used: Optional[str] = None
    created_at: datetime


class ScoreRecordOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    score: int
    reasoning: Optional[str] = None
    factors: Dict[str, Any] = {}
    created_at: datetime


class GeneratedMessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    channel: str
    message_type: str
    content: str
    status: str
    created_at: datetime


class ProspectContactDetailOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    company_id: str
    full_name: str
    title: Optional[str] = None
    linkedin_url: Optional[str] = None
    email: Optional[str] = None
    scores: List[ScoreRecordOut] = []
    messages: List[GeneratedMessageOut] = []


class ProspectCompanyOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    icp_id: str
    name: str
    website: Optional[str] = None
    industry: Optional[str] = None
    location: Optional[str] = None
    employee_count: Optional[int] = None
    stage: str
    created_at: datetime
    contacts: List[ProspectContactOut] = []
    research_records: List[ResearchRecordOut] = []


class JobOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    job_type: str
    entity_type: str
    entity_id: str
    status: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class ApprovalDecision(BaseModel):
    reviewer: str
    edited_content: Optional[str] = None
    reason: Optional[str] = None
