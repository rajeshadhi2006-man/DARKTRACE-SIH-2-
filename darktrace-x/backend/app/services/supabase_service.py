import os
import time
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import httpx
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("darktrace.supabase")

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://surihwgxgymlgdxyghqx.supabase.co")
SUPABASE_ANON_KEY = os.getenv(
    "SUPABASE_ANON_KEY",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InN1cmlod2d4Z3ltbGdkeHlnaHF4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTA0OTg2MTIsImV4cCI6MjEwNjA3NDYxMn0.e24rW2AqxaCs6ODLhlSzIqOjEQd3DRfVH6I7mzcleHM"
)

_client: Optional[Client] = None

def get_supabase_client() -> Client:
    global _client
    if _client is None:
        try:
            _client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
            logger.info("Supabase client initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")
            raise
    return _client

def check_supabase_health() -> Dict[str, Any]:
    """Tests connection to Supabase and measures latency."""
    start_time = time.time()
    try:
        with httpx.Client(timeout=3.0) as client:
            resp = client.get(
                f"{SUPABASE_URL}/auth/v1/health",
                headers={
                    "apikey": SUPABASE_ANON_KEY,
                    "Authorization": f"Bearer {SUPABASE_ANON_KEY}"
                }
            )
            latency_ms = round((time.time() - start_time) * 1000, 2)
            if resp.status_code == 200:
                return {
                    "status": "HEALTHY",
                    "connected": True,
                    "url": SUPABASE_URL,
                    "project_ref": "surihwgxgymlgdxyghqx",
                    "latency_ms": latency_ms,
                    "auth_service": "ONLINE",
                    "realtime": "ONLINE",
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                }
            else:
                return {
                    "status": "DEGRADED",
                    "connected": False,
                    "url": SUPABASE_URL,
                    "error": f"HTTP {resp.status_code}",
                    "latency_ms": latency_ms,
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                }
    except Exception as e:
        latency_ms = round((time.time() - start_time) * 1000, 2)
        return {
            "status": "UNHEALTHY",
            "connected": False,
            "url": SUPABASE_URL,
            "error": str(e),
            "latency_ms": latency_ms,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

def save_threat_broadcast_to_supabase(data: Dict[str, Any]) -> bool:
    """Inserts a threat broadcast into the Supabase threat_broadcasts table."""
    try:
        client = get_supabase_client()
        client.table("threat_broadcasts").insert({
            "threat_type": data.get("threat_type", "ANOMALY"),
            "severity": data.get("severity", "HIGH"),
            "source": data.get("source", "DARKNET_MONITOR"),
            "actor": data.get("actor", "UNKNOWN"),
            "summary": data.get("summary", ""),
            "metadata": data.get("metadata", {})
        }).execute()
        logger.info("Threat broadcast saved to Supabase cloud.")
        return True
    except Exception as e:
        logger.warning(f"Could not persist threat broadcast to Supabase: {e}")
        return False

def save_ai_analysis_to_supabase(analysis: Dict[str, Any]) -> bool:
    """Inserts or updates an AI correlation assessment into Supabase ai_analyses table."""
    try:
        client = get_supabase_client()
        rel = analysis.get("candidate_relationships", [{}])[0]
        client.table("ai_analyses").upsert({
            "id": analysis.get("analysis_id", f"ANL-{int(time.time())}"),
            "investigation_id": analysis.get("investigation_id", "INV-SIH-001"),
            "persona_a": rel.get("entity_a", "persona_a"),
            "persona_b": rel.get("entity_b", "persona_b"),
            "overall_score": float(rel.get("overall_score", 0.0)),
            "confidence_level": rel.get("confidence_level", "unknown"),
            "identifier_score": float(rel.get("identifier_score", 0.0)),
            "behavior_score": float(rel.get("behavior_score", 0.0)),
            "linguistic_score": float(rel.get("linguistic_score", 0.0)),
            "infrastructure_score": float(rel.get("infrastructure_score", 0.0)),
            "temporal_score": float(rel.get("temporal_score", 0.0)),
            "gemini_explanation": rel.get("explanation", ""),
            "key_observations": rel.get("key_observations", []),
            "contradictory_evidence": rel.get("contradictory_evidence", []),
            "missing_evidence": rel.get("missing_evidence", []),
            "evidence_citations": rel.get("evidence_ids", []),
            "disclaimer": analysis.get("disclaimer", "Analytical correlation — not confirmed real-world attribution.")
        }).execute()
        logger.info(f"AI analysis {analysis.get('analysis_id')} synced to Supabase.")
        return True
    except Exception as e:
        logger.warning(f"Could not persist AI analysis to Supabase: {e}")
        return False

