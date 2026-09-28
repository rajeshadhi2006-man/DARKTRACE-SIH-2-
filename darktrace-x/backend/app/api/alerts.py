from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database.connection import get_db
from ..models.entities import Alert, Actor, AuditLog
from ..security.auth import get_current_user

router = APIRouter(prefix="/alerts", tags=["Threat Intelligence Alerts & Anomaly Warnings"])

@router.get("")
def list_alerts(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    alerts = db.query(Alert).order_by(Alert.created_at.desc()).all()
    results = []
    for alt in alerts:
        actor_name = None
        if alt.actor_id:
            act = db.query(Actor).filter(Actor.id == alt.actor_id).first()
            if act:
                actor_name = act.primary_name

        results.append({
            "id": alt.id,
            "title": alt.title,
            "event_type": alt.event_type,
            "actor_id": alt.actor_id,
            "actor_name": actor_name,
            "persona_id": alt.persona_id,
            "severity": alt.severity,
            "confidence": alt.confidence,
            "description": alt.description,
            "supporting_evidence_count": alt.supporting_evidence_count,
            "status": alt.status,
            "created_at": alt.created_at
        })
    return results

@router.post("/{alert_id}/ack")
def acknowledge_alert(
    alert_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    alt = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alt:
        raise HTTPException(status_code=404, detail="Alert not found")

    alt.status = "ACKNOWLEDGED"

    audit = AuditLog(
        user_id=current_user.id,
        action="ALERT_ACKNOWLEDGED",
        object_type="Alert",
        object_id=alt.id,
        details={"title": alt.title, "event_type": alt.event_type}
    )
    db.add(audit)
    db.commit()

    return {"status": "ACKNOWLEDGED", "alert_id": alt.id}

@router.post("/ack-all")
def acknowledge_all_alerts(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    unacked = db.query(Alert).filter(Alert.status == "NEW").all()
    for alt in unacked:
        alt.status = "ACKNOWLEDGED"

    from ..models.entities import AttributionAssessment
    assessments = db.query(AttributionAssessment).filter(AttributionAssessment.is_confirmed_by_analyst == False).all()
    for a in assessments:
        a.is_confirmed_by_analyst = True

    db.commit()

    try:
        from ..services.realtime.manager import ws_manager
        from ..models.entities import IntelligenceRecord, Evidence
        total_records = db.query(IntelligenceRecord).count()
        total_evidence = db.query(Evidence).count()
        ws_manager.broadcast_sync({
            "type": "KPI_TELEMETRY_UPDATE",
            "metrics": {
                "total_intelligence_records": total_records,
                "evidence_items": total_evidence,
                "unresolved_alerts": 0,
            }
        })
    except Exception:
        pass

    return {"status": "ACKNOWLEDGED_ALL", "cleared_count": len(unacked), "unresolved_remaining": 0}

