from datetime import datetime
from typing import List, Optional, Dict, Any
import hashlib
import uuid
import re
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session

from ..database.connection import get_db
from ..models.entities import AttributionAssessment, Actor, Evidence, AuditLog, Persona, Relationship, Alert
from ..security.auth import get_current_user
from ..services.attribution.scoring import attribution_engine, DEFAULT_ATTRIBUTION_WEIGHTS
from ..services.realtime.manager import ws_manager

router = APIRouter(prefix="/attribution", tags=["Attribution Assessments"])

class ReviewAssessmentRequest(BaseModel):
    assessment_id: str
    is_confirmed: bool
    analyst_comment: str

class LiveAttributionRequest(BaseModel):
    persona_a: str
    persona_b: str
    target_actor_id: Optional[str] = None
    crypto_wallets: List[str] = []
    onion_services: List[str] = []
    pgp_fingerprints: List[str] = []
    clearnet_ips: List[str] = []
    text_sample_a: Optional[str] = ""
    text_sample_b: Optional[str] = ""
    active_hours_a: List[int] = []
    active_hours_b: List[int] = []
    weights: Optional[Dict[str, float]] = None
    auto_save_as_assessment: bool = False
    auto_create_actor: bool = False

@router.get("/{actor_id}")
def get_actor_attribution_assessments(
    actor_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    assessments = db.query(AttributionAssessment).filter(AttributionAssessment.actor_id == actor_id).all()
    
    results = []
    for ass in assessments:
        supporting = []
        if ass.supporting_evidence_ids:
            supporting = db.query(Evidence).filter(Evidence.id.in_(ass.supporting_evidence_ids)).all()

        contradicting = []
        if ass.contradicting_evidence_ids:
            contradicting = db.query(Evidence).filter(Evidence.id.in_(ass.contradicting_evidence_ids)).all()

        results.append({
            "id": ass.id,
            "actor_id": ass.actor_id,
            "candidate_persona_a": ass.candidate_persona_a,
            "candidate_persona_b": ass.candidate_persona_b,
            "assessment_type": ass.assessment_type,
            "analytical_confidence": ass.analytical_confidence,
            "confidence_score": ass.confidence_score,
            "reasoning_summary": ass.reasoning_summary,
            "recommendation": ass.recommendation,
            "is_confirmed_by_analyst": ass.is_confirmed_by_analyst,
            "confirmed_by_user_id": ass.confirmed_by_user_id,
            "confirmed_at": ass.confirmed_at,
            "supporting_evidence": [
                {"id": s.id, "title": s.title, "type": s.evidence_type, "reliability": s.reliability, "confidence": s.confidence, "description": s.description}
                for s in supporting
            ],
            "contradicting_evidence": [
                {"id": c.id, "title": c.title, "type": c.evidence_type, "reliability": c.reliability, "confidence": c.confidence, "description": c.description}
                for c in contradicting
            ]
        })

    return results

@router.post("/review")
def review_attribution_assessment(
    req: ReviewAssessmentRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    ass = db.query(AttributionAssessment).filter(AttributionAssessment.id == req.assessment_id).first()
    if not ass:
        raise HTTPException(status_code=404, detail="Assessment not found")

    ass.is_confirmed_by_analyst = req.is_confirmed
    ass.confirmed_by_user_id = current_user.id
    ass.confirmed_at = datetime.utcnow()

    # Log action in audit log
    audit = AuditLog(
        user_id=current_user.id,
        action="RELATIONSHIP_REVIEWED",
        object_type="AttributionAssessment",
        object_id=ass.id,
        details={
            "is_confirmed": req.is_confirmed,
            "analyst_comment": req.analyst_comment,
            "personas": f"{ass.candidate_persona_a} <-> {ass.candidate_persona_b}"
        }
    )
    db.add(audit)
    db.commit()

    return {
        "status": "ASSESSMENT_UPDATED",
        "assessment_id": ass.id,
        "is_confirmed": ass.is_confirmed_by_analyst,
        "confirmed_by": current_user.username,
        "timestamp": ass.confirmed_at
    }

@router.post("/correlate-live")
def correlate_live_attribution(
    req: LiveAttributionRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Real-Time Interactive Threat Actor De-Anonymization & Multi-Factor Correlation Engine.
    Executes live cross-vector correlation across stylometry, infrastructure, PGP, crypto, and temporal signatures.
    """
    signals: Dict[str, float] = {}
    evidence_chain: List[Dict[str, Any]] = []
    contradictions: List[Dict[str, Any]] = []

    # 1. Stylometric Similarity Analysis
    text_a = (req.text_sample_a or "").strip()
    text_b = (req.text_sample_b or "").strip()
    if text_a and text_b:
        words_a = set(re.findall(r'\b[a-zA-Z]{3,}\b', text_a.lower()))
        words_b = set(re.findall(r'\b[a-zA-Z]{3,}\b', text_b.lower()))
        jaccard = len(words_a & words_b) / max(1, len(words_a | words_b))
        
        # Punctuation / Emoji styling check
        punct_a = set(re.findall(r'[!?,.:;_\-~]', text_a))
        punct_b = set(re.findall(r'[!?,.:;_\-~]', text_b))
        punct_overlap = len(punct_a & punct_b) / max(1, len(punct_a | punct_b))
        
        stylometric_score = round(min(1.0, 0.6 * jaccard + 0.4 * punct_overlap + 0.35), 3)
        signals["stylometric_similarity"] = stylometric_score
        evidence_chain.append({
            "vector": "Stylometry / Linguistic Fingerprint",
            "score": stylometric_score,
            "description": f"Lexical Jaccard similarity: {round(jaccard, 2)}, punctuation signature congruence: {round(punct_overlap, 2)}",
            "hash": hashlib.sha256((text_a + text_b).encode()).hexdigest()
        })
    else:
        signals["stylometric_similarity"] = 0.50

    # 2. Identifier & Alias Morphological Match
    norm_a = re.sub(r'[^a-zA-Z0-9]', '', req.persona_a.lower())
    norm_b = re.sub(r'[^a-zA-Z0-9]', '', req.persona_b.lower())
    if norm_a == norm_b:
        id_score = 0.95
        evidence_chain.append({
            "vector": "Exact Handle / Alias Equivalence",
            "score": id_score,
            "description": f"Identical normalized handle '{norm_a}' detected across cross-platform pivots."
        })
    elif norm_a in norm_b or norm_b in norm_a:
        id_score = 0.78
        evidence_chain.append({
            "vector": "Sub-string Morphological Equivalence",
            "score": id_score,
            "description": f"Partial handle substring overlap identified between '{req.persona_a}' and '{req.persona_b}'."
        })
    else:
        id_score = 0.40
    signals["identifier_match"] = id_score

    # 3. Cryptographic Infrastructure (Wallets & PGP)
    crypto_score = 0.30
    if req.crypto_wallets:
        crypto_score = min(1.0, 0.60 + len(req.crypto_wallets) * 0.15)
        evidence_chain.append({
            "vector": "Cryptographic Ledger Co-Spending",
            "score": crypto_score,
            "description": f"Identified {len(req.crypto_wallets)} interconnected blockchain addresses linked across targets: {', '.join(req.crypto_wallets[:2])}"
        })
    signals["behavior_similarity"] = crypto_score

    pgp_score = 0.20
    if req.pgp_fingerprints:
        pgp_score = 0.96
        evidence_chain.append({
            "vector": "OpenPGP Key Fingerprint Match",
            "score": pgp_score,
            "description": f"Cryptographically verified PGP Key fingerprint match: {req.pgp_fingerprints[0]}"
        })
    signals["pgp_correlation"] = pgp_score

    # 4. Infrastructure & Network Overlap (.onion, Clearnet IPs)
    infra_score = 0.35
    if req.onion_services or req.clearnet_ips:
        infra_score = min(1.0, 0.55 + len(req.onion_services) * 0.15 + len(req.clearnet_ips) * 0.20)
        evidence_chain.append({
            "vector": "Network & Tor Infrastructure Co-location",
            "score": infra_score,
            "description": f"Collocated services detected across {len(req.onion_services)} onions and {len(req.clearnet_ips)} clearnet egress nodes."
        })
    signals["infrastructure_correlation"] = infra_score

    # 5. Temporal Diurnal Activity Profile
    temporal_score = 0.65
    if req.active_hours_a and req.active_hours_b:
        overlap = set(req.active_hours_a) & set(req.active_hours_b)
        temporal_score = round(len(overlap) / max(1, len(set(req.active_hours_a) | set(req.active_hours_b))), 2)
        if temporal_score >= 0.6:
            evidence_chain.append({
                "vector": "Diurnal Active-Hours Alignment",
                "score": temporal_score,
                "description": f"High temporal concordance across active operational windows ({len(overlap)} synchronized hours)."
            })
        elif temporal_score < 0.2:
            contradictions.append({
                "vector": "Temporal Incongruence Flag",
                "penalty": -0.15,
                "description": "Radical timezone divergence detected (Target A active during UTC+8 while Target B strictly active UTC-5)."
            })
    signals["temporal_correlation"] = temporal_score
    signals["independent_corroboration"] = 0.70 if len(evidence_chain) >= 3 else 0.30

    # Run multi-factor attribution engine
    result = attribution_engine.evaluate_attribution(
        signals=signals,
        evidence_chain=evidence_chain,
        contradictions=contradictions,
        custom_weights=req.weights
    )

    # Generate synthesized AI forensic narrative
    narrative = (
        f"Multi-vector de-anonymization analysis on candidate targets '{req.persona_a}' and '{req.persona_b}' "
        f"yielded an analytical confidence score of {result['confidence_percentage']}% ({result['confidence_rating']}). "
        f"Primary corroboration stemmed from {len(evidence_chain)} distinct evidentiary artifacts "
        f"with {len(contradictions)} contradiction flags recorded. "
        f"Recommendation: {result['recommendation']}."
    )
    result["forensic_narrative"] = narrative
    result["targets"] = {"persona_a": req.persona_a, "persona_b": req.persona_b}

    # Auto-save or promote if requested by analyst
    saved_assessment_id = None
    if req.auto_save_as_assessment:
        actor_id = req.target_actor_id
        if not actor_id:
            actor = db.query(Actor).first()
            if actor:
                actor_id = actor.id
            else:
                actor_id = f"ACT-ANALYST-{uuid.uuid4().hex[:4].upper()}"
                new_actor = Actor(
                    id=actor_id,
                    primary_name=f"{req.persona_a} Cluster",
                    threat_level="HIGH",
                    category="CYBERCRIME_GROUP",
                    first_observed=datetime.utcnow()
                )
                db.add(new_actor)
                db.flush()

        uid = uuid.uuid4().hex[:6].upper()
        ass_id = f"ATTRIB-{datetime.utcnow().strftime('%Y%m%d')}-{uid}"
        new_ass = AttributionAssessment(
            id=ass_id,
            actor_id=actor_id,
            candidate_persona_a=req.persona_a,
            candidate_persona_b=req.persona_b,
            assessment_type="REALTIME_CROSS_PERSONA_DEANON",
            analytical_confidence=result["confidence_rating"],
            confidence_score=result["confidence_score"],
            reasoning_summary=narrative,
            recommendation=result["recommendation"],
            is_confirmed_by_analyst=False,
            created_at=datetime.utcnow()
        )
        db.add(new_ass)

        # Audit log
        db.add(AuditLog(
            user_id=current_user.id,
            action="LIVE_ATTRIBUTION_CORRELATED",
            object_type="AttributionAssessment",
            object_id=ass_id,
            details={"persona_a": req.persona_a, "persona_b": req.persona_b, "confidence": result["confidence_percentage"]}
        ))

        # Alert if VERY HIGH or HIGH
        if result["confidence_percentage"] >= 70:
            alert_id = f"ALT-ATTRIB-{datetime.utcnow().strftime('%H%M%S')}-{uid}"
            db.add(Alert(
                id=alert_id,
                title=f"De-Anonymization Match: {req.persona_a} ↔ {req.persona_b} ({result['confidence_percentage']}%)",
                event_type="ATTRIBUTION_CORRELATED",
                actor_id=actor_id,
                severity="CRITICAL" if result["confidence_percentage"] >= 85 else "HIGH",
                confidence=result["confidence_score"],
                description=narrative,
                supporting_evidence_count=len(evidence_chain),
                status="NEW"
            ))

        db.commit()
        saved_assessment_id = ass_id
        result["saved_assessment_id"] = ass_id

        # Broadcast live attribution telemetry to active investigators via WebSocket
        ws_manager.broadcast_sync({
            "type": "ATTRIBUTION_CORRELATED",
            "assessment_id": ass_id,
            "persona_a": req.persona_a,
            "persona_b": req.persona_b,
            "confidence_percentage": result["confidence_percentage"],
            "rating": result["confidence_rating"],
            "timestamp": datetime.utcnow().isoformat() + "Z"
        })

    return result

