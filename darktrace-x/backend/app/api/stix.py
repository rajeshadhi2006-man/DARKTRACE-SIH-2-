from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
import json

from ..database.connection import get_db
from ..models.entities import Actor, Persona, Wallet, Domain, Infrastructure, Campaign, AuditLog
from ..security.auth import get_current_user
from ..services.reporting.stix_generator import stix_generator

router = APIRouter(prefix="/stix", tags=["STIX 2.1 Threat Intelligence Export"])

@router.get("/actor/{actor_id}")
def export_actor_stix_bundle(
    actor_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Exports a threat actor, associated personas, wallets, domains, and infrastructure
    as an OASIS STIX 2.1 JSON compliant bundle.
    """
    actor = db.query(Actor).filter(Actor.id == actor_id).first()
    if not actor:
        raise HTTPException(status_code=404, detail="Threat actor not found")

    personas = db.query(Persona).filter(Persona.actor_id == actor.id).all()
    
    # Collect indicators
    indicators = []
    wallets = db.query(Wallet).all()
    for w in wallets:
        indicators.append({"type": f"Cryptocurrency-{w.currency}", "value": w.address})

    domains = db.query(Domain).all()
    for d in domains:
        indicators.append({"type": "Domain-Onion" if d.is_onion else "Domain-Clearnet", "value": d.domain_name})

    infras = db.query(Infrastructure).all()
    for inf in infras:
        if inf.clearnet_correlation:
            indicators.append({"type": "IP", "value": inf.clearnet_correlation})

    campaign = db.query(Campaign).first()

    bundle = stix_generator.generate_bundle(
        actor={
            "id": actor.id,
            "primary_name": actor.primary_name,
            "threat_category": actor.threat_category,
            "threat_level": actor.threat_level,
            "confidence_score": actor.confidence_score,
            "summary": actor.summary
        },
        personas=[{"canonical_handle": p.canonical_handle} for p in personas],
        indicators=indicators[:10],
        relationships=[],
        campaign={
            "id": campaign.id,
            "name": campaign.name,
            "description": campaign.description,
            "confidence": campaign.confidence
        } if campaign else None
    )

    # Log audit
    audit = AuditLog(
        user_id=current_user.id,
        action="STIX_BUNDLE_EXPORTED",
        object_type="Actor",
        object_id=actor.id,
        details={"bundle_id": bundle["id"], "objects_count": len(bundle["objects"])}
    )
    db.add(audit)
    db.commit()

    return Response(
        content=json.dumps(bundle, indent=2),
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename={actor.id}_STIX21_Bundle.json"}
    )
