from fastapi import APIRouter, HTTPException
from typing import Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime

from ..services.supabase_service import get_supabase_client, check_supabase_health, SUPABASE_URL

router = APIRouter(prefix="/supabase", tags=["Supabase Integration"])

class ThreatBroadcastRequest(BaseModel):
    threat_type: str
    severity: str = "HIGH"
    source: str = "DARKNET_CRAWLER"
    actor: str = "UNKNOWN"
    summary: str

@router.get("/status")
def get_supabase_status():
    """Returns current Supabase connection health, latency, and status."""
    return check_supabase_health()

@router.get("/config")
def get_supabase_public_config():
    """Returns public config for Supabase client connection."""
    return {
        "url": SUPABASE_URL,
        "project_ref": "surihwgxgymlgdxyghqx",
        "realtime_enabled": True
    }

@router.post("/broadcast")
async def broadcast_threat(payload: ThreatBroadcastRequest):
    """Broadcasts a high-priority threat alert to Supabase Realtime channel and all consoles."""
    event_payload = {
        "threat_type": payload.threat_type,
        "severity": payload.severity,
        "source": payload.source,
        "actor": payload.actor,
        "summary": payload.summary,
        "cloud_sync": "SUPABASE_REALTIME",
        "project_ref": "surihwgxgymlgdxyghqx",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

    # Save to Supabase table
    try:
        from ..services.supabase_service import save_threat_broadcast_to_supabase
        save_threat_broadcast_to_supabase(event_payload)
    except Exception:
        pass

    # Also broadcast directly to connected frontend telemetry WebSockets
    try:
        from ..services.realtime.manager import ws_manager
        await ws_manager.broadcast({
            "type": "NEW_THREAT_DETECTED",
            "data": event_payload
        })
    except Exception:
        pass

    return {
        "status": "BROADCAST_SENT",
        "channel": "darktrace-telemetry-feed",
        "event": "threat_alert",
        "cloud": "SUPABASE_ACTIVE",
        "data": event_payload
    }
