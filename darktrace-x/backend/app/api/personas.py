from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database.connection import get_db
from ..models.entities import Persona, StylometricProfile, BehaviorProfile
from ..security.auth import get_current_user

router = APIRouter(prefix="/personas", tags=["Personas"])

@router.get("")
def list_personas(
    platform: Optional[str] = Query(None),
    actor_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    q = db.query(Persona)
    if platform:
        q = q.filter(Persona.platform.ilike(f"%{platform}%"))
    if actor_id:
        q = q.filter(Persona.actor_id == actor_id)

    personas = q.order_by(Persona.activity_count.desc()).all()
    results = []
    for p in personas:
        results.append({
            "id": p.id,
            "canonical_handle": p.canonical_handle,
            "platform": p.platform,
            "actor_id": p.actor_id,
            "first_seen": p.first_seen,
            "last_seen": p.last_seen,
            "activity_count": p.activity_count,
            "confidence": p.confidence,
            "reliability": p.reliability,
            "handles": [h.original_value for h in p.handles]
        })
    return results

@router.get("/{persona_id}")
def get_persona(
    persona_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    p = db.query(Persona).filter(Persona.id == persona_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Persona not found")

    sp = db.query(StylometricProfile).filter(StylometricProfile.persona_id == p.id).first()
    bp = db.query(BehaviorProfile).filter(BehaviorProfile.persona_id == p.id).first()

    return {
        "id": p.id,
        "canonical_handle": p.canonical_handle,
        "platform": p.platform,
        "actor_id": p.actor_id,
        "first_seen": p.first_seen,
        "last_seen": p.last_seen,
        "activity_count": p.activity_count,
        "confidence": p.confidence,
        "reliability": p.reliability,
        "provenance": p.provenance,
        "handles": [{"original": h.original_value, "normalized": h.normalized_value, "platform": h.platform} for h in p.handles],
        "stylometric_profile": {
            "sample_count": sp.sample_count,
            "avg_sentence_length": sp.avg_sentence_length,
            "avg_word_length": sp.avg_word_length,
            "lexical_diversity_ttr": sp.lexical_diversity_ttr,
            "punctuation_entropy": sp.punctuation_entropy,
            "uppercase_ratio": sp.uppercase_ratio,
            "function_word_frequencies": sp.function_word_frequencies,
            "characteristic_jargon": sp.characteristic_jargon
        } if sp else None,
        "behavior_profile": {
            "active_hours_distribution": bp.active_hours_distribution,
            "peak_active_utc": bp.peak_active_utc,
            "estimated_timezone": bp.estimated_timezone,
            "posting_interval_mean_hours": bp.posting_interval_mean_hours,
            "platform_migration_cadence": bp.platform_migration_cadence
        } if bp else None
    }
