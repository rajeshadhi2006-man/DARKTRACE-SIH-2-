from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional

from ..services.realtime.crawler_daemon import realtime_daemon
from ..database.connection import SessionLocal
from ..services.ingestion.collector import autonomous_collector
from ..security.auth import get_current_user
from ..models.entities import (
    Actor, Persona, Handle, PGPKey, Wallet, Domain, Infrastructure,
    IntelligenceRecord, Evidence, Relationship, TimelineEvent,
    StylometricProfile, BehaviorProfile, AttributionAssessment, AnalystNote,
    Investigation, Campaign, Alert, MitreTechnique
)
from ..database.seed_data import seed_complete_synthetic_intelligence
from ..services.realtime.manager import ws_manager

router = APIRouter(prefix="/realtime", tags=["Real-Time Crawler & Telemetry"])

class IntervalRequest(BaseModel):
    interval_seconds: float

@router.get("/status")
def get_daemon_status():
    """Returns current real-time crawler daemon status, cycle count, cadence, and active connections."""
    return realtime_daemon.get_status()

@router.post("/start")
def start_daemon():
    """Starts the real-time crawler daemon."""
    realtime_daemon.start()
    return {"message": "Real-time crawler daemon initiated", "status": realtime_daemon.get_status()}

@router.post("/stop")
def stop_daemon():
    """Stops the real-time crawler daemon."""
    realtime_daemon.stop()
    return {"message": "Real-time crawler daemon halted", "status": realtime_daemon.get_status()}

@router.post("/config")
def update_daemon_config(req: IntervalRequest):
    """Updates crawl cadence (in seconds)."""
    realtime_daemon.set_interval(req.interval_seconds)
    return {"message": f"Interval set to {realtime_daemon.interval_seconds}s", "status": realtime_daemon.get_status()}

@router.post("/trigger")
def trigger_instant_intercept():
    """Manually triggers an immediate darknet sensor sweep outside of regular interval."""
    db = SessionLocal()
    try:
        res = autonomous_collector.trigger_crawler_cycle(db, user_id="MANUAL_ANALYST_TRIGGER")
        return {"status": "SUCCESS", "intercept": res}
    finally:
        db.close()

@router.post("/reset")
def reset_realtime_metrics():
    """Resets the live crawler cycle count to 0 and clears temporary telemetry caches."""
    realtime_daemon.cycle_count = 0
    realtime_daemon.last_intercept = None
    return {"message": "Cycle count and telemetry counter reset to 0", "status": realtime_daemon.get_status()}

@router.post("/clear-all-to-zero")
def clear_all_to_zero():
    """Wipes all threat intelligence data, resetting ALL metric values in the system to 0."""
    db = SessionLocal()
    try:
        # Delete data in child-first order to satisfy foreign keys
        db.query(TimelineEvent).delete()
        db.query(AnalystNote).delete()
        db.query(AttributionAssessment).delete()
        db.query(BehaviorProfile).delete()
        db.query(StylometricProfile).delete()
        db.query(Relationship).delete()
        db.query(Evidence).delete()
        db.query(IntelligenceRecord).delete()
        db.query(Alert).delete()
        db.query(Campaign).delete()
        db.query(Investigation).delete()
        db.query(MitreTechnique).delete()
        db.query(Infrastructure).delete()
        db.query(Domain).delete()
        db.query(Wallet).delete()
        db.query(PGPKey).delete()
        db.query(Handle).delete()
        db.query(Persona).delete()
        db.query(Actor).delete()
        db.commit()

        # Reset real-time daemon state to 0
        realtime_daemon.cycle_count = 0
        realtime_daemon.last_intercept = None

        # Broadcast 0s to all connected WebSocket clients
        ws_manager.broadcast_sync({
            "type": "KPI_TELEMETRY_UPDATE",
            "metrics": {
                "total_intelligence_records": 0,
                "evidence_items": 0,
                "unresolved_alerts": 0
            }
        })

        return {
            "status": "ALL_VALUES_RESET_TO_ZERO",
            "message": "All threat intelligence metrics, actors, personas, and records have become 0."
        }
    finally:
        db.close()

@router.post("/reseed-demo-data")
def reseed_demo_data():
    """Restores the complete synthetic threat intelligence demo dataset."""
    db = SessionLocal()
    try:
        seed_complete_synthetic_intelligence(db)
        total_records = db.query(IntelligenceRecord).count()
        total_evidence = db.query(Evidence).count()
        total_alerts = db.query(Alert).filter(Alert.status == "NEW").count()

        ws_manager.broadcast_sync({
            "type": "KPI_TELEMETRY_UPDATE",
            "metrics": {
                "total_intelligence_records": total_records,
                "evidence_items": total_evidence,
                "unresolved_alerts": total_alerts
            }
        })

        return {
            "status": "DEMO_DATA_RESTORED",
            "message": "Complete 21 threat actor demo intelligence dataset restored successfully."
        }
    finally:
        db.close()
