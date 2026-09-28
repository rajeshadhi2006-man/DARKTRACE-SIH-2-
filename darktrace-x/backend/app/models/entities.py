import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, Text, DateTime, ForeignKey, JSON
)
from sqlalchemy.orm import relationship
from ..database.connection import Base

def gen_uuid():
    return str(uuid.uuid4())

def gen_id(prefix: str):
    return lambda: f"{prefix}-{uuid.uuid4().hex[:10].upper()}"

def utc_now():
    return datetime.utcnow()

# ============================================================
# USER & RBAC MODELS
# ============================================================

class Role(Base):
    __tablename__ = "roles"

    id = Column(String(50), primary_key=True)  # ADMIN, SUPERVISOR, ANALYST, VIEWER
    description = Column(String(255))
    permissions = Column(JSON, default=list)  # list of permission strings

    users = relationship("User", back_populates="role")

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    role_id = Column(String(50), ForeignKey("roles.id"), default="ANALYST")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utc_now)
    last_login = Column(DateTime, nullable=True)

    role = relationship("Role", back_populates="users")
    notes = relationship("AnalystNote", back_populates="author")
    audit_logs = relationship("AuditLog", back_populates="user")

# ============================================================
# CORE THREAT INTELLIGENCE & ENTITY MODELS
# ============================================================

class Source(Base):
    __tablename__ = "sources"

    id = Column(String(100), primary_key=True)  # e.g., SRC-DREAD, SRC-BREACHFORUMS
    name = Column(String(255), nullable=False)
    source_type = Column(String(100))  # FORUM, MARKETPLACE, PASTE, OSINT, SENSOR
    url_or_onion = Column(String(500), nullable=True)
    reliability = Column(String(20), default="B")  # A (Confirmed), B (Usually reliable), C (Fairly reliable), etc.
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

class Actor(Base):
    __tablename__ = "actors"

    id = Column(String(50), primary_key=True, default=gen_id("ACT"))  # e.g., ACT-0042
    primary_name = Column(String(255), nullable=False, index=True)
    threat_category = Column(String(100), default="UNKNOWN")  # Ransomware, IAB, Carding, etc.
    threat_level = Column(String(20), default="MEDIUM")  # CRITICAL, HIGH, MEDIUM, LOW
    status = Column(String(50), default="ACTIVE")  # ACTIVE, DORMANT, REBRANDED, ARRESTED
    analytical_confidence = Column(String(20), default="MEDIUM")  # HIGH, MEDIUM, LOW
    confidence_score = Column(Float, default=0.5)  # 0.0 to 1.0
    first_observed = Column(DateTime, nullable=True)
    last_observed = Column(DateTime, nullable=True)
    summary = Column(Text, nullable=True)
    provenance = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    personas = relationship("Persona", back_populates="actor")
    notes = relationship("AnalystNote", back_populates="actor")
    assessments = relationship("AttributionAssessment", back_populates="actor")
    timeline_events = relationship("TimelineEvent", back_populates="actor")

class Persona(Base):
    __tablename__ = "personas"

    id = Column(String(50), primary_key=True, default=gen_id("PER"))  # e.g. PER-0101
    actor_id = Column(String(50), ForeignKey("actors.id"), nullable=True)
    canonical_handle = Column(String(255), nullable=False, index=True)
    platform = Column(String(100))  # Dread, Exploit.in, BreachForums, etc.
    first_seen = Column(DateTime, nullable=True)
    last_seen = Column(DateTime, nullable=True)
    activity_count = Column(Integer, default=0)
    source_id = Column(String(100), ForeignKey("sources.id"), nullable=True)
    confidence = Column(Float, default=0.8)
    reliability = Column(String(20), default="B")
    provenance = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    actor = relationship("Actor", back_populates="personas")
    handles = relationship("Handle", back_populates="persona")
    stylometric_profile = relationship("StylometricProfile", back_populates="persona", uselist=False)
    behavior_profile = relationship("BehaviorProfile", back_populates="persona", uselist=False)

class Handle(Base):
    __tablename__ = "handles"

    id = Column(String(50), primary_key=True, default=gen_id("HDL"))
    persona_id = Column(String(50), ForeignKey("personas.id"), nullable=True)
    original_value = Column(String(255), nullable=False)
    normalized_value = Column(String(255), nullable=False, index=True)
    platform = Column(String(100), nullable=True)
    source_id = Column(String(100), ForeignKey("sources.id"), nullable=True)
    confidence = Column(Float, default=0.9)
    reliability = Column(String(20), default="A")
    provenance = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    persona = relationship("Persona", back_populates="handles")

class PGPKey(Base):
    __tablename__ = "pgp_keys"

    id = Column(String(50), primary_key=True, default=gen_id("KEY"))  # KEY-001
    key_id = Column(String(32), index=True)
    fingerprint = Column(String(100), unique=True, index=True)
    algorithm = Column(String(50), default="RSA")
    bit_length = Column(Integer, default=4096)
    identity_email = Column(String(255), nullable=True)
    raw_public_key = Column(Text, nullable=True)
    source_id = Column(String(100), ForeignKey("sources.id"), nullable=True)
    confidence = Column(Float, default=1.0)
    reliability = Column(String(20), default="A")
    provenance = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

class Wallet(Base):
    __tablename__ = "wallets"

    id = Column(String(50), primary_key=True, default=gen_id("WLT"))  # WALLET-001
    currency = Column(String(20), nullable=False)  # BTC, XMR, ETH, USDT
    address = Column(String(255), unique=True, index=True, nullable=False)
    cluster_tags = Column(JSON, default=list)
    total_received_approx = Column(String(100), nullable=True)
    source_id = Column(String(100), ForeignKey("sources.id"), nullable=True)
    confidence = Column(Float, default=0.95)
    reliability = Column(String(20), default="A")
    provenance = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

class Domain(Base):
    __tablename__ = "domains"

    id = Column(String(50), primary_key=True, default=gen_id("DOM"))
    domain_name = Column(String(500), index=True, nullable=False)
    is_onion = Column(Boolean, default=False)
    resolved_ip = Column(String(100), nullable=True)
    nameservers = Column(JSON, default=list)
    source_id = Column(String(100), ForeignKey("sources.id"), nullable=True)
    confidence = Column(Float, default=0.9)
    reliability = Column(String(20), default="B")
    provenance = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

class Infrastructure(Base):
    __tablename__ = "infrastructure"

    id = Column(String(50), primary_key=True, default=gen_id("INF"))  # INF-001
    indicator_type = Column(String(100))  # IP, SSL_CERT_SAN, FAVICON_MURMUR3, SSH_BANNER, VHOST
    indicator_value = Column(String(500), index=True, nullable=False)
    clearnet_correlation = Column(String(255), nullable=True)
    asn_isp = Column(String(255), nullable=True)
    country = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True)
    details = Column(JSON, default=dict)
    source_id = Column(String(100), ForeignKey("sources.id"), nullable=True)
    confidence = Column(Float, default=0.85)
    reliability = Column(String(20), default="B")
    provenance = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

class IntelligenceRecord(Base):
    __tablename__ = "observations"

    id = Column(String(50), primary_key=True, default=gen_id("OBS"))  # OBS-001 or INTEL-001
    source_id = Column(String(100), ForeignKey("sources.id"), nullable=True)
    record_type = Column(String(100))  # FORUM_POST, MARKET_LISTING, RECON_SCAN, EXTORTION_NOTE
    author_raw = Column(String(255), nullable=True)
    content_raw = Column(Text, nullable=False)
    content_sha256 = Column(String(64), index=True)
    extracted_entities = Column(JSON, default=dict)
    timestamp = Column(DateTime, default=utc_now)
    collection_timestamp = Column(DateTime, default=utc_now)
    confidence = Column(Float, default=0.85)
    reliability = Column(String(20), default="B")
    provenance = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

class Evidence(Base):
    __tablename__ = "evidence"

    id = Column(String(50), primary_key=True, default=gen_id("EVID"))  # EVID-0001
    source_id = Column(String(100), ForeignKey("sources.id"), nullable=True)
    observation_id = Column(String(50), ForeignKey("observations.id"), nullable=True)
    evidence_type = Column(String(100))  # IDENTITY, INFRASTRUCTURE, CONTENT, BEHAVIOR, HISTORICAL
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    content_hash = Column(String(64), nullable=False)  # SHA-256 for integrity verification
    timestamp = Column(DateTime, default=utc_now)
    collection_timestamp = Column(DateTime, default=utc_now)
    reliability = Column(String(20), default="A")  # A, B, C
    confidence = Column(Float, default=0.9)
    related_entity_ids = Column(JSON, default=list)
    provenance = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

class Relationship(Base):
    __tablename__ = "relationships"

    id = Column(String(50), primary_key=True, default=gen_id("REL"))  # REL-0001
    source_entity_id = Column(String(100), index=True, nullable=False)
    target_entity_id = Column(String(100), index=True, nullable=False)
    relationship_type = Column(String(100), nullable=False)  # USES, ASSOCIATED_WITH, CONNECTED_TO, SIMILAR_TO, MIGRATED_TO
    confidence = Column(Float, default=0.75)
    reliability = Column(String(20), default="B")
    evidence_id = Column(String(50), ForeignKey("evidence.id"), nullable=True)
    source_id = Column(String(100), ForeignKey("sources.id"), nullable=True)
    timestamp = Column(DateTime, default=utc_now)
    collection_timestamp = Column(DateTime, default=utc_now)
    provenance = Column(Text, nullable=True)
    properties = Column(JSON, default=dict)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

class TimelineEvent(Base):
    __tablename__ = "timeline_events"

    id = Column(String(50), primary_key=True, default=gen_id("TML"))  # TML-0001
    actor_id = Column(String(50), ForeignKey("actors.id"), nullable=True)
    persona_id = Column(String(50), ForeignKey("personas.id"), nullable=True)
    event_type = Column(String(100), nullable=False)  # ACCOUNT_CREATION, PGP_OBSERVED, WALLET_TRANS, INFRA_EVENT, MIGRATION
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    event_timestamp = Column(DateTime, nullable=False, index=True)
    source_id = Column(String(100), ForeignKey("sources.id"), nullable=True)
    evidence_id = Column(String(50), ForeignKey("evidence.id"), nullable=True)
    confidence = Column(Float, default=0.85)
    reliability = Column(String(20), default="B")
    provenance = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    actor = relationship("Actor", back_populates="timeline_events")

# ============================================================
# ANALYTICS & PROFILING MODELS
# ============================================================

class StylometricProfile(Base):
    __tablename__ = "stylometric_profiles"

    id = Column(String(50), primary_key=True, default=gen_id("STY"))
    persona_id = Column(String(50), ForeignKey("personas.id"), unique=True)
    sample_count = Column(Integer, default=0)
    avg_sentence_length = Column(Float, default=0.0)
    avg_word_length = Column(Float, default=0.0)
    lexical_diversity_ttr = Column(Float, default=0.0)
    punctuation_entropy = Column(Float, default=0.0)
    uppercase_ratio = Column(Float, default=0.0)
    function_word_frequencies = Column(JSON, default=dict)
    characteristic_jargon = Column(JSON, default=list)
    char_ngram_signature = Column(JSON, default=dict)
    provenance = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    persona = relationship("Persona", back_populates="stylometric_profile")

class BehaviorProfile(Base):
    __tablename__ = "behavior_profiles"

    id = Column(String(50), primary_key=True, default=gen_id("BEH"))
    persona_id = Column(String(50), ForeignKey("personas.id"), unique=True)
    active_hours_distribution = Column(JSON, default=list)  # 24-hr histogram
    peak_active_utc = Column(Integer, nullable=True)
    estimated_timezone = Column(String(50), nullable=True)
    posting_interval_mean_hours = Column(Float, default=0.0)
    platform_migration_cadence = Column(String(100), nullable=True)
    anomalies_detected = Column(JSON, default=list)
    provenance = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    persona = relationship("Persona", back_populates="behavior_profile")

class AttributionAssessment(Base):
    __tablename__ = "attribution_assessments"

    id = Column(String(50), primary_key=True, default=gen_id("ATTR"))  # ATTR-0001
    actor_id = Column(String(50), ForeignKey("actors.id"), nullable=False)
    candidate_persona_a = Column(String(100), nullable=False)
    candidate_persona_b = Column(String(100), nullable=False)
    assessment_type = Column(String(100), default="POTENTIAL_PERSONA_RELATIONSHIP")
    analytical_confidence = Column(String(20), default="MEDIUM")  # LOW, MEDIUM, HIGH
    confidence_score = Column(Float, default=0.65)
    supporting_evidence_ids = Column(JSON, default=list)
    contradicting_evidence_ids = Column(JSON, default=list)
    reasoning_summary = Column(Text, nullable=False)
    recommendation = Column(String(100), default="MANUAL_INVESTIGATOR_REVIEW")
    is_confirmed_by_analyst = Column(Boolean, default=False)
    confirmed_by_user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    confirmed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    actor = relationship("Actor", back_populates="assessments")

class AnalystNote(Base):
    __tablename__ = "analyst_notes"

    id = Column(String(50), primary_key=True, default=gen_id("NOTE"))
    actor_id = Column(String(50), ForeignKey("actors.id"), nullable=True)
    evidence_id = Column(String(50), ForeignKey("evidence.id"), nullable=True)
    author_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    classification = Column(String(50), default="TLP:AMBER")
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    actor = relationship("Actor", back_populates="notes")
    author = relationship("User", back_populates="notes")

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(50), primary_key=True, default=gen_id("AUDIT"))  # AUDIT-0001
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    action = Column(String(100), nullable=False)  # LOGIN, LOGOUT, ACTOR_VIEW, EVIDENCE_VIEW, SEARCH, REPORT_GEN
    object_type = Column(String(100), nullable=True)  # Actor, Evidence, Search, Assessment
    object_id = Column(String(100), nullable=True)
    details = Column(JSON, default=dict)
    ip_address = Column(String(50), nullable=True)
    session_id = Column(String(100), nullable=True)
    timestamp = Column(DateTime, default=utc_now, index=True)

    user = relationship("User", back_populates="audit_logs")

class ReportRecord(Base):
    __tablename__ = "reports"

    id = Column(String(50), primary_key=True, default=gen_id("REP"))  # REP-0001
    title = Column(String(255), nullable=False)
    report_type = Column(String(50), default="INVESTIGATION_DOSSIER")  # PDF, CSV, JSON, STIX
    actor_id = Column(String(50), ForeignKey("actors.id"), nullable=True)
    file_path = Column(String(500), nullable=True)
    file_size_bytes = Column(Integer, default=0)
    file_hash_sha256 = Column(String(64), nullable=True)
    generated_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    classification = Column(String(50), default="LAW ENFORCEMENT SENSITIVE // TLP:AMBER")
    created_at = Column(DateTime, default=utc_now)


# ============================================================
# INVESTIGATION, CASE & CAMPAIGN MODELS
# ============================================================

class Investigation(Base):
    __tablename__ = "investigations"

    id = Column(String(50), primary_key=True, default=gen_id("INV"))  # INV-2026-001
    case_id = Column(String(50), index=True, nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    analyst_name = Column(String(100), default="Lead CTI Analyst")
    assigned_user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    status = Column(String(50), default="ACTIVE")  # ACTIVE, REVIEW, CLOSED, REOPENED
    priority = Column(String(20), default="HIGH")  # CRITICAL, HIGH, MEDIUM, LOW
    scope = Column(String(255), default="Dark Web Threat Actor De-Anonymization")
    seed_indicators = Column(JSON, default=list)  # list of {type: 'alias', value: 'nightfox_404'}
    extracted_entities = Column(JSON, default=list)
    findings = Column(JSON, default=list)
    actor_id = Column(String(50), ForeignKey("actors.id"), nullable=True)
    confidence_assessment = Column(Float, default=0.0)
    start_date = Column(DateTime, default=utc_now)
    end_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)


class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(String(50), primary_key=True, default=gen_id("CMP"))  # CMP-001
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    threat_actor_ids = Column(JSON, default=list)
    target_sectors = Column(JSON, default=list)
    infrastructure_indicators = Column(JSON, default=list)
    mitre_techniques = Column(JSON, default=list)
    first_seen = Column(DateTime, nullable=True)
    last_seen = Column(DateTime, nullable=True)
    confidence = Column(Float, default=0.85)
    status = Column(String(50), default="ACTIVE")  # ACTIVE, DORMANT, DISRUPTED
    evidence_ids = Column(JSON, default=list)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(String(50), primary_key=True, default=gen_id("ALT"))  # ALT-0001
    title = Column(String(255), nullable=False)
    event_type = Column(String(100), nullable=False)  # PERSONA_MIGRATION, HIGH_CONFIDENCE_CORRELATION, INFRA_PIVOT, CONTRADICTION_FLAG
    actor_id = Column(String(50), ForeignKey("actors.id"), nullable=True)
    persona_id = Column(String(50), ForeignKey("personas.id"), nullable=True)
    severity = Column(String(20), default="HIGH")  # CRITICAL, HIGH, MEDIUM, LOW
    confidence = Column(Float, default=0.8)
    description = Column(Text, nullable=False)
    supporting_evidence_count = Column(Integer, default=1)
    status = Column(String(50), default="NEW")  # NEW, ACKNOWLEDGED, RESOLVED
    created_at = Column(DateTime, default=utc_now)


class MitreTechnique(Base):
    __tablename__ = "mitre_techniques"

    id = Column(String(50), primary_key=True)  # T1566.001
    name = Column(String(255), nullable=False)
    tactic = Column(String(100), nullable=False)  # Initial Access, Defense Evasion, etc.
    description = Column(Text, nullable=True)
    associated_actors = Column(JSON, default=list)
    evidence_references = Column(JSON, default=list)
    confidence = Column(Float, default=0.85)
    created_at = Column(DateTime, default=utc_now)

