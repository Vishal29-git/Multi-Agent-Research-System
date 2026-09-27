from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, JSON, Float
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid
from backend.database.session import Base

def generate_uuid():
    return str(uuid.uuid4())

class ResearchSession(Base):
    __tablename__ = "research_sessions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    query = Column(Text, nullable=False)
    status = Column(String(50), default="queued") # queued, running, completed, failed
    current_agent = Column(String(50), default="waiting")
    progress_percent = Column(Integer, default=0)
    iterations = Column(Integer, default=0)
    report_markdown = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    tasks = relationship("ResearchTask", back_populates="session", cascade="all, delete-orphan")
    findings = relationship("ResearchFinding", back_populates="session", cascade="all, delete-orphan")
    claims = relationship("VerifiedClaim", back_populates="session", cascade="all, delete-orphan")
    sources = relationship("Source", back_populates="session", cascade="all, delete-orphan")

class ResearchTask(Base):
    __tablename__ = "research_tasks"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    session_id = Column(String(36), ForeignKey("research_sessions.id"), nullable=False)
    topic = Column(Text, nullable=False)
    assigned_agent = Column(String(100), nullable=True)
    status = Column(String(50), default="pending") # pending, running, completed, failed
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    session = relationship("ResearchSession", back_populates="tasks")

class ResearchFinding(Base):
    __tablename__ = "research_findings"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    session_id = Column(String(36), ForeignKey("research_sessions.id"), nullable=False)
    topic = Column(Text, nullable=False)
    findings_json = Column(JSON, default=list)
    claims_json = Column(JSON, default=list)
    sources_json = Column(JSON, default=list)
    confidence = Column(String(20), default="medium")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    session = relationship("ResearchSession", back_populates="findings")

class VerifiedClaim(Base):
    __tablename__ = "verified_claims"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    session_id = Column(String(36), ForeignKey("research_sessions.id"), nullable=False)
    claim = Column(Text, nullable=False)
    status = Column(String(50), default="unsupported") # Supported, Partially Supported, Unsupported, Contradicted
    evidence_json = Column(JSON, default=list)
    confidence = Column(String(20), default="medium")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    session = relationship("ResearchSession", back_populates="claims")

class Source(Base):
    __tablename__ = "sources"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    session_id = Column(String(36), ForeignKey("research_sessions.id"), nullable=False)
    title = Column(Text, nullable=False)
    url = Column(Text, nullable=False)
    snippet = Column(Text, nullable=True)
    relevance_score = Column(Float, default=1.0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    session = relationship("ResearchSession", back_populates="sources")
