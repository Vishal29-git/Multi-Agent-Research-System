from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict
from datetime import datetime

class ResearchRequest(BaseModel):
    query: str = Field(..., example="How could AGI emerge in the future?")

class SourceSchema(BaseModel):
    id: Optional[str] = None
    title: str
    url: str
    snippet: Optional[str] = None
    relevance_score: Optional[float] = 1.0

    class Config:
        from_attributes = True

class VerifiedClaimSchema(BaseModel):
    id: Optional[str] = None
    claim: str
    status: str # Supported, Partially Supported, Unsupported, Contradicted
    evidence: List[str] = []
    confidence: str # high, medium, low

    class Config:
        from_attributes = True

class ResearchFindingSchema(BaseModel):
    topic: str
    findings: List[str] = []
    claims: List[str] = []
    sources: List[SourceSchema] = []
    confidence: str = "medium"

    class Config:
        from_attributes = True

class AgentStatusSchema(BaseModel):
    name: str
    status: str # waiting, running, completed, failed
    activity: str
    progress: int

class SessionStatusResponse(BaseModel):
    id: str
    query: str
    status: str
    current_agent: str
    progress_percent: int
    iterations: int
    agents: List[AgentStatusSchema]
    sources_count: int
    claims_count: int
    verified_claims_count: int
    report_markdown: Optional[str] = None
    error_message: Optional[str] = None

    class Config:
        from_attributes = True

class SessionDetailResponse(BaseModel):
    id: str
    query: str
    status: str
    progress_percent: int
    iterations: int
    report_markdown: Optional[str] = None
    sources: List[SourceSchema] = []
    claims: List[VerifiedClaimSchema] = []
    created_at: datetime

    class Config:
        from_attributes = True

class SessionSummaryResponse(BaseModel):
    id: str
    query: str
    status: str
    progress_percent: int
    created_at: datetime

    class Config:
        from_attributes = True
