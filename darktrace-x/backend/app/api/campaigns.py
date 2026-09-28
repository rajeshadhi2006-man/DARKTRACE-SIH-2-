from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database.connection import get_db
from ..models.entities import Campaign, Actor, Evidence
from ..security.auth import get_current_user

router = APIRouter(prefix="/campaigns", tags=["Threat Campaigns & Activity Clusters"])

@router.get("")
def list_campaigns(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    campaigns = db.query(Campaign).order_by(Campaign.created_at.desc()).all()
    results = []
    for cmp in campaigns:
        actors = []
        if cmp.threat_actor_ids:
            actors = db.query(Actor).filter(Actor.id.in_(cmp.threat_actor_ids)).all()

        results.append({
            "id": cmp.id,
            "name": cmp.name,
            "description": cmp.description,
            "threat_actors": [{"id": a.id, "name": a.primary_name, "level": a.threat_level} for a in actors],
            "target_sectors": cmp.target_sectors or [],
            "infrastructure_indicators": cmp.infrastructure_indicators or [],
            "mitre_techniques": cmp.mitre_techniques or [],
            "confidence": cmp.confidence,
            "status": cmp.status,
            "first_seen": cmp.first_seen,
            "last_seen": cmp.last_seen
        })
    return results

@router.get("/{campaign_id}")
def get_campaign_detail(
    campaign_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    cmp = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not cmp:
        raise HTTPException(status_code=404, detail="Campaign not found")

    actors = []
    if cmp.threat_actor_ids:
        actors = db.query(Actor).filter(Actor.id.in_(cmp.threat_actor_ids)).all()

    evidence_items = []
    if cmp.evidence_ids:
        evidence_items = db.query(Evidence).filter(Evidence.id.in_(cmp.evidence_ids)).all()

    return {
        "id": cmp.id,
        "name": cmp.name,
        "description": cmp.description,
        "threat_actors": [{"id": a.id, "name": a.primary_name, "category": a.threat_category, "level": a.threat_level} for a in actors],
        "target_sectors": cmp.target_sectors or [],
        "infrastructure_indicators": cmp.infrastructure_indicators or [],
        "mitre_techniques": cmp.mitre_techniques or [],
        "confidence": cmp.confidence,
        "status": cmp.status,
        "first_seen": cmp.first_seen,
        "last_seen": cmp.last_seen,
        "evidence": [
            {"id": e.id, "title": e.title, "type": e.evidence_type, "confidence": e.confidence}
            for e in evidence_items
        ]
    }
