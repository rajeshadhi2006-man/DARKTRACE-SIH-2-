from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session
from sqlalchemy import or_

from ..database.connection import get_db
from ..models.entities import Actor, Persona, Handle, PGPKey, Wallet, Infrastructure, Evidence, AuditLog
from ..security.auth import get_current_user

router = APIRouter(prefix="/search", tags=["Global Search"])

@router.get("")
def global_search(
    q: str = Query(..., min_length=2, description="Query handles, PGP, wallets, IPs, actors, or evidence"),
    entity_type: Optional[str] = Query(None),
    limit: int = 40,
    request: Request = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    query_str = q.strip()
    results: List[Dict[str, Any]] = []

    # 1. Search Actors
    if not entity_type or entity_type.upper() == "ACTOR":
        actors = db.query(Actor).filter(
            or_(Actor.primary_name.ilike(f"%{query_str}%"), Actor.id.ilike(f"%{query_str}%"))
        ).limit(10).all()
        for a in actors:
            results.append({
                "type": "Actor",
                "id": a.id,
                "title": a.primary_name,
                "subtitle": f"{a.threat_category} • {a.threat_level}",
                "confidence": a.confidence_score,
                "url": f"/actors/{a.id}"
            })

    # 2. Search Personas & Handles
    if not entity_type or entity_type.upper() in ["PERSONA", "HANDLE"]:
        personas = db.query(Persona).filter(
            or_(Persona.canonical_handle.ilike(f"%{query_str}%"), Persona.id.ilike(f"%{query_str}%"))
        ).limit(10).all()
        for p in personas:
            results.append({
                "type": "Persona",
                "id": p.id,
                "title": p.canonical_handle,
                "subtitle": f"Platform: {p.platform} • Actor: {p.actor_id or 'Unlinked'}",
                "confidence": p.confidence,
                "url": f"/personas/{p.id}"
            })

    # 3. Search PGP Keys
    if not entity_type or entity_type.upper() == "PGP":
        pgps = db.query(PGPKey).filter(
            or_(PGPKey.fingerprint.ilike(f"%{query_str}%"), PGPKey.key_id.ilike(f"%{query_str}%"))
        ).limit(10).all()
        for k in pgps:
            results.append({
                "type": "PGPKey",
                "id": k.id,
                "title": f"PGP Key: {k.key_id}",
                "subtitle": f"Fingerprint: {k.fingerprint}",
                "confidence": k.confidence,
                "url": f"/search?q={k.key_id}"
            })

    # 4. Search Wallets
    if not entity_type or entity_type.upper() == "WALLET":
        wallets = db.query(Wallet).filter(Wallet.address.ilike(f"%{query_str}%")).limit(10).all()
        for w in wallets:
            results.append({
                "type": "Wallet",
                "id": w.id,
                "title": f"{w.currency} Address",
                "subtitle": w.address,
                "confidence": w.confidence,
                "url": f"/search?q={w.address}"
            })

    # 5. Search Infrastructure
    if not entity_type or entity_type.upper() == "INFRASTRUCTURE":
        infras = db.query(Infrastructure).filter(
            or_(Infrastructure.indicator_value.ilike(f"%{query_str}%"), Infrastructure.clearnet_correlation.ilike(f"%{query_str}%"))
        ).limit(10).all()
        for inf in infras:
            results.append({
                "type": "Infrastructure",
                "id": inf.id,
                "title": f"{inf.indicator_type}: {inf.indicator_value}",
                "subtitle": f"ASN: {inf.asn_isp or 'N/A'} • {inf.country or ''}",
                "confidence": inf.confidence,
                "url": f"/infrastructure"
            })

    # 6. Search Evidence
    if not entity_type or entity_type.upper() == "EVIDENCE":
        evs = db.query(Evidence).filter(
            or_(Evidence.title.ilike(f"%{query_str}%"), Evidence.id.ilike(f"%{query_str}%"), Evidence.description.ilike(f"%{query_str}%"))
        ).limit(10).all()
        for ev in evs:
            results.append({
                "type": "Evidence",
                "id": ev.id,
                "title": ev.title,
                "subtitle": f"{ev.evidence_type} • Reliability: {ev.reliability}",
                "confidence": ev.confidence,
                "url": f"/evidence/{ev.id}"
            })

    # Log search in audit
    if request:
        audit = AuditLog(
            user_id=current_user.id,
            action="SEARCH",
            object_type="SearchQuery",
            object_id=query_str,
            details={"results_count": len(results)},
            ip_address=request.client.host if request.client else "127.0.0.1"
        )
        db.add(audit)
        db.commit()

    return {
        "query": query_str,
        "total_results": len(results),
        "results": results[:limit]
    }
