from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class EntityObservation(BaseModel):
    type: str  # "handle", "pgp", "wallet", "email", "domain", "certificate", "ip"
    value: str
    source: str
    timestamp: Optional[str] = None
    evidence_id: Optional[str] = None

class BehaviorFeatures(BaseModel):
    active_hours: List[str] = Field(default_factory=list)
    posting_frequency: float = 0.0
    topics: List[str] = Field(default_factory=list)
    activity_days: Optional[List[str]] = Field(default_factory=list)

class LanguageFeatures(BaseModel):
    average_sentence_length: float = 0.0
    punctuation_pattern: str = ""
    common_terms: List[str] = Field(default_factory=list)
    vocabulary_diversity: Optional[float] = 0.0
    repeated_phrases: Optional[List[str]] = Field(default_factory=list)
    writing_embedding_reference: Optional[str] = None

class InfrastructureIndicator(BaseModel):
    type: str  # "certificate", "asn", "nameserver", "ip", "banner"
    fingerprint: str
    details: Optional[Dict[str, Any]] = Field(default_factory=dict)
    evidence_id: Optional[str] = None

class StructuredInvestigation(BaseModel):
    investigation_id: str
    persona_a: str
    persona_b: Optional[str] = None
    entities: List[EntityObservation] = Field(default_factory=list)
    behavior: BehaviorFeatures = Field(default_factory=BehaviorFeatures)
    language_features: LanguageFeatures = Field(default_factory=LanguageFeatures)
    infrastructure: List[InfrastructureIndicator] = Field(default_factory=list)
    evidence_pool: Optional[List[Dict[str, Any]]] = Field(default_factory=list)

class CandidateRelationship(BaseModel):
    entity_a: str
    entity_b: str
    relationship_type: str = "possible_same_persona"
    identifier_score: float
    behavior_score: float
    linguistic_score: float
    infrastructure_score: float
    temporal_score: float
    overall_score: float
    confidence_level: str  # "weak_correlation", "possible_correlation", "strong_correlation", "very_strong_correlation", "insufficient_evidence"
    key_observations: List[str] = Field(default_factory=list)
    contradictory_evidence: List[str] = Field(default_factory=list)
    missing_evidence: List[str] = Field(default_factory=list)
    evidence_ids: List[str] = Field(default_factory=list)
    explanation: str
    provenance_chain: Optional[List[Dict[str, Any]]] = Field(default_factory=list)

class PatternAnalysisResponse(BaseModel):
    analysis_id: str
    investigation_id: str
    engine: str = "Gemini-2.5-Flash + Deterministic Pattern Pipeline"
    candidate_relationships: List[CandidateRelationship] = Field(default_factory=list)
    unrelated_entities: List[str] = Field(default_factory=list)
    recommended_investigation_steps: List[str] = Field(default_factory=list)
    evidence_quality: str = "medium"
    disclaimer: str = "Analytical correlation — not confirmed real-world attribution."
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")

class ActorComparisonRequest(BaseModel):
    actor_id_a: str
    actor_id_b: str
    investigation_id: Optional[str] = "INV-AUTO-COMPARE"
    include_ai_reasoning: bool = True
