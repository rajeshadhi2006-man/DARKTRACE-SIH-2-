from typing import List, Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database.connection import get_db
from ..models.entities import MitreTechnique, Actor, Evidence
from ..security.auth import get_current_user

router = APIRouter(prefix="/mitre", tags=["MITRE ATT&CK Framework Mapping"])

@router.get("")
def list_mitre_techniques(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    techniques = db.query(MitreTechnique).all()
    results = []
    for t in techniques:
        actors = []
        if t.associated_actors:
            actors = db.query(Actor).filter(Actor.id.in_(t.associated_actors)).all()

        evidence_items = []
        if t.evidence_references:
            evidence_items = db.query(Evidence).filter(Evidence.id.in_(t.evidence_references)).all()

        results.append({
            "id": t.id,
            "name": t.name,
            "tactic": t.tactic,
            "description": t.description,
            "confidence": t.confidence,
            "associated_actors": [{"id": a.id, "name": a.primary_name, "level": a.threat_level} for a in actors],
            "evidence": [{"id": e.id, "title": e.title, "confidence": e.confidence} for e in evidence_items],
            "created_at": t.created_at
        })
    return results
