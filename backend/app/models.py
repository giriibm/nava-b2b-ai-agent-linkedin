"""
SQLAlchemy models mirroring the Data Model in the Master Spec (§9).
Every table carries an organization_id boundary so Phase 3 multi-tenancy
does not require a schema rewrite.
"""
import uuid
import enum
from datetime import datetime

from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Text, JSON, Enum
)
from sqlalchemy.orm import relationship

from app.database import Base


def gen_id() -> str:
    return str(uuid.uuid4())


class ProspectStage(str, enum.Enum):
    discovered = "discovered"
    researched = "researched"
    scored = "scored"
    approved = "approved"
    contacted = "contacted"
    replied = "replied"
    converted = "converted"


class MessageStatus(str, enum.Enum):
    draft = "draft"
    approved = "approved"
    edited = "edited"
    rejected = "rejected"
    sent = "sent"


class Channel(str, enum.Enum):
    linkedin = "linkedin"
    email = "email"


class Organization(Base):
    __tablename__ = "organizations"
    id = Column(String, primary_key=True, default=gen_id)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    icps = relationship("ICP", back_populates="organization")


class ICP(Base):
    __tablename__ = "icps"
    id = Column(String, primary_key=True, default=gen_id)
    organization_id = Column(String, ForeignKey("organizations.id"), nullable=False)
    name = Column(String, nullable=False)
    industry = Column(String)
    geography = Column(String)
    company_size_range = Column(String)
    revenue_range = Column(String)
    target_roles = Column(JSON, default=list)
    keywords = Column(JSON, default=list)
    business_challenges = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)

    organization = relationship("Organization", back_populates="icps")
    companies = relationship("ProspectCompany", back_populates="icp")


class ProspectCompany(Base):
    __tablename__ = "prospect_companies"
    id = Column(String, primary_key=True, default=gen_id)
    icp_id = Column(String, ForeignKey("icps.id"), nullable=False)
    name = Column(String, nullable=False)
    website = Column(String)
    industry = Column(String)
    location = Column(String)
    employee_count = Column(Integer)
    source = Column(String, default="linkedin_sales_navigator_export")
    salesforce_account_id = Column(String, nullable=True)
    stage = Column(Enum(ProspectStage), default=ProspectStage.discovered)
    created_at = Column(DateTime, default=datetime.utcnow)

    icp = relationship("ICP", back_populates="companies")
    contacts = relationship("ProspectContact", back_populates="company")
    research_records = relationship("ResearchRecord", back_populates="company")


class ProspectContact(Base):
    __tablename__ = "prospect_contacts"
    id = Column(String, primary_key=True, default=gen_id)
    company_id = Column(String, ForeignKey("prospect_companies.id"), nullable=False)
    full_name = Column(String, nullable=False)
    title = Column(String)
    linkedin_url = Column(String)
    email = Column(String, nullable=True)
    salesforce_lead_id = Column(String, nullable=True)
    salesforce_contact_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    company = relationship("ProspectCompany", back_populates="contacts")
    scores = relationship("ScoreRecord", back_populates="contact")
    messages = relationship("GeneratedMessage", back_populates="contact")


class ResearchRecord(Base):
    __tablename__ = "research_records"
    id = Column(String, primary_key=True, default=gen_id)
    prospect_company_id = Column(String, ForeignKey("prospect_companies.id"), nullable=False)
    summary = Column(Text)
    business_challenges = Column(JSON, default=list)
    ai_opportunity_areas = Column(JSON, default=list)
    recommended_solution = Column(Text)
    model_used = Column(String)
    prompt_version = Column(String, default="v1")
    created_at = Column(DateTime, default=datetime.utcnow)

    company = relationship("ProspectCompany", back_populates="research_records")


class ScoreRecord(Base):
    __tablename__ = "score_records"
    id = Column(String, primary_key=True, default=gen_id)
    prospect_contact_id = Column(String, ForeignKey("prospect_contacts.id"), nullable=False)
    score = Column(Integer)
    reasoning = Column(Text)
    factors = Column(JSON, default=dict)
    model_used = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    contact = relationship("ProspectContact", back_populates="scores")


class GeneratedMessage(Base):
    __tablename__ = "generated_messages"
    id = Column(String, primary_key=True, default=gen_id)
    prospect_contact_id = Column(String, ForeignKey("prospect_contacts.id"), nullable=False)
    channel = Column(Enum(Channel), default=Channel.linkedin)
    message_type = Column(String)  # connection_request | initial_message | follow_up | subject_line | email_body
    content = Column(Text)
    status = Column(Enum(MessageStatus), default=MessageStatus.draft)
    approved_by = Column(String, nullable=True)
    approved_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    contact = relationship("ProspectContact", back_populates="messages")
    outreach_activities = relationship("OutreachActivity", back_populates="message")


class OutreachActivity(Base):
    __tablename__ = "outreach_activities"
    id = Column(String, primary_key=True, default=gen_id)
    generated_message_id = Column(String, ForeignKey("generated_messages.id"), nullable=False)
    sent_at = Column(DateTime, nullable=True)
    delivery_channel = Column(String)  # heyreach | email_platform
    salesforce_task_id = Column(String, nullable=True)
    reply_received = Column(Boolean, default=False)
    reply_classification = Column(String, nullable=True)

    message = relationship("GeneratedMessage", back_populates="outreach_activities")


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(String, primary_key=True, default=gen_id)
    entity_type = Column(String, nullable=False)
    entity_id = Column(String, nullable=False)
    action = Column(String, nullable=False)
    actor = Column(String, default="system")
    payload = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)


class Job(Base):
    """Tracks async AI agent jobs (research / score / generate-message)."""
    __tablename__ = "jobs"
    id = Column(String, primary_key=True, default=gen_id)
    job_type = Column(String, nullable=False)
    entity_type = Column(String, nullable=False)
    entity_id = Column(String, nullable=False)
    status = Column(String, default="pending")  # pending | running | completed | failed
    result = Column(JSON, nullable=True)
    error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
