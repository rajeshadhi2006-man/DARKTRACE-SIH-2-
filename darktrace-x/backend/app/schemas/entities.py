from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

# ----------------- Auth & User Schemas -----------------
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]

class TokenPayload(BaseModel):
    sub: Optional[str] = None
    role: Optional[str] = None
    exp: Optional[int] = None

class LoginRequest(BaseModel):
    username: str
    password: str

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: str
    role_id: str = "ANALYST"

class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    full_name: Optional[str]
    role_id: str
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True

class ActorCreate(BaseModel):
    id: Optional[str] = None
    primary_name: str
    threat_category: str = "Uncategorized"
    threat_level: str = "MEDIUM"
    status: str = "ACTIVE"
    confidence_score: float = 0.70
    summary: Optional[str] = None
    provenance: Optional[str] = "Manual entry"

class AnalystNoteCreate(BaseModel):
    content: str
    title: Optional[str] = "Analyst Observation"
    classification: Optional[str] = "RESTRICTED"

class ActorSummary(BaseModel):
    id: str
    primary_name: str
    threat_category: str
    threat_level: str
    status: str
    analytical_confidence: str
    confidence_score: float
    first_observed: Optional[datetime] = None
    last_observed: Optional[datetime] = None
    persona_count: int = 0
    evidence_count: int = 0

class PersonaResponse(BaseModel):
    id: str
    actor_id: Optional[str] = None
    canonical_handle: str
    platform: Optional[str] = None
    first_seen: Optional[datetime] = None
    last_seen: Optional[datetime] = None
    activity_count: int = 0
    confidence: float
    reliability: str
    provenance: Optional[str] = None

class EvidenceResponse(BaseModel):
    id: str
    source_id: Optional[str]
    evidence_type: str
    title: str
    description: str
    content_hash: str
    timestamp: datetime
    reliability: str
    confidence: float
    related_entity_ids: List[str] = []
    provenance: Optional[str] = None

class RelationshipResponse(BaseModel):
    id: str
    source_entity_id: str
    target_entity_id: str
    relationship_type: str
    confidence: float
    reliability: str
    evidence_id: Optional[str] = None
    source_id: Optional[str] = None
    timestamp: datetime
    properties: Dict[str, Any] = {}

class TimelineEventResponse(BaseModel):
    id: str
    actor_id: Optional[str] = None
    persona_id: Optional[str] = None
    event_type: str
    title: str
    description: Optional[str] = None
    event_timestamp: datetime
    source_id: Optional[str] = None
    evidence_id: Optional[str] = None
    confidence: float

class AttributionAssessmentResponse(BaseModel):
    id: str
    actor_id: str
    candidate_persona_a: str
    candidate_persona_b: str
    assessment_type: str
    analytical_confidence: str
    confidence_score: float
    supporting_evidence_ids: List[str] = []
    contradicting_evidence_ids: List[str] = []
    reasoning_summary: str
    recommendation: str
    is_confirmed_by_analyst: bool = False
    confirmed_by_user_id: Optional[str] = None
    confirmed_at: Optional[datetime] = None

class DashboardStats(BaseModel):
    total_actors: int
    total_personas: int
    total_handles: int
    total_intelligence_records: int
    total_relationships: int
    potential_persona_links: int
    infrastructure_relationships: int
    pending_reviews: int
    evidence_items: int
    source_distribution: Dict[str, int]
    confidence_distribution: Dict[str, int]
    activity_over_time: List[Dict[str, Any]]
    recent_findings: List[Dict[str, Any]]

class HealthCheckResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str = "1.0.0"
    database: Dict[str, Any]
    graph_db: Dict[str, Any]
    cache: Dict[str, Any]
