import asyncio
import logging
import random
import uuid
from datetime import datetime
from typing import Optional

from ...database.connection import SessionLocal
from ...models.entities import IntelligenceRecord, Evidence, Alert, Actor
from ..ingestion.collector import autonomous_collector
from .manager import ws_manager

logger = logging.getLogger("darktrace.crawler_daemon")

class RealtimeCrawlerDaemon:
    """
    Continuous Real-Time Darknet Crawler & Telemetry Broadcast Daemon.
    Harvests simulated authorized intercepts every few seconds, indexes indicators,
    triggers anomaly alerts, and streams live telemetry to investigator consoles via WebSocket.
    """

    def __init__(self, interval_seconds: float = 5.0):
        self.interval_seconds = interval_seconds
        self.is_running = False
        self._task: Optional[asyncio.Task] = None
        self.cycle_count = 0
        self.last_run_timestamp: Optional[str] = None
        self.last_intercept: Optional[dict] = None

    def start(self):
        if not self.is_running:
            self.is_running = True
            self._task = asyncio.create_task(self._run_loop())
            logger.info(f"Real-Time Crawler Daemon started (Cadence: {self.interval_seconds}s).")

    def stop(self):
        self.is_running = False
        if self._task and not self._task.done():
            self._task.cancel()
        logger.info("Real-Time Crawler Daemon stopped.")

    def set_interval(self, seconds: float):
        self.interval_seconds = max(1.0, min(60.0, float(seconds)))
        logger.info(f"Real-Time Crawler Daemon interval updated to {self.interval_seconds}s.")

    def get_status(self) -> dict:
        return {
            "is_running": self.is_running,
            "interval_seconds": self.interval_seconds,
            "cycle_count": self.cycle_count,
            "last_run": self.last_run_timestamp,
            "active_ws_subscribers": len(ws_manager.active_connections),
            "last_intercept": self.last_intercept
        }

    async def _run_loop(self):
        # Initial sleep to allow complete application initialization and database seeding
        await asyncio.sleep(2.0)

        while self.is_running:
            try:
                db = SessionLocal()
                try:
                    res = autonomous_collector.trigger_crawler_cycle(db, user_id="DAEMON_AUTONOMOUS_WORKER")
                    self.cycle_count += 1
                    self.last_run_timestamp = datetime.utcnow().isoformat() + "Z"
                    self.last_intercept = res

                    # Inspect author & indicators to generate contextual real-time alerts
                    author = res.get("author", "")
                    source = res.get("source", "")
                    indicators = res.get("extracted_indicators", {})

                    if any(k in author for k in ["KernelPanik", "ViperZero", "VoidReaper"]):
                        uid = uuid.uuid4().hex[:6].upper()
                        alert_id = f"ALT-LIVE-{datetime.utcnow().strftime('%H%M%S')}-{uid}"
                        actor_id = "ACT-001" if "ViperZero" in author else ("ACT-002" if "KernelPanik" in author else None)
                        
                        alt = Alert(
                            id=alert_id,
                            title=f"Live Threat Intercept: High-Risk Activity by {author}",
                            event_type="REALTIME_INTERCEPT_FLAG",
                            actor_id=actor_id,
                            severity="HIGH" if "0day" not in author else "CRITICAL",
                            confidence=0.89,
                            description=(
                                f"Autonomous darknet sensor captured live underground transmission on {source} "
                                f"authored by '{author}'. Extracted {len(indicators.get('btc_wallets', []))} BTC, "
                                f"{len(indicators.get('xmr_wallets', []))} XMR, {len(indicators.get('onion_services', []))} Onions, "
                                f"and {len(indicators.get('clearnet_ips', []))} Clearnet IP pivots."
                            ),
                            supporting_evidence_count=1,
                            status="NEW"
                        )
                        db.add(alt)
                        db.commit()

                        # Broadcast live alert to investigator WebSocket feeds
                        await ws_manager.broadcast({
                            "type": "NEW_ALERT",
                            "alert": {
                                "id": alert_id,
                                "title": alt.title,
                                "severity": alt.severity,
                                "confidence": alt.confidence,
                                "event_type": alt.event_type,
                                "actor_id": actor_id,
                                "actor_name": author,
                                "description": alt.description,
                                "supporting_evidence_count": 1,
                                "status": "NEW",
                                "created_at": datetime.utcnow().isoformat() + "Z"
                            }
                        })

                    # Broadcast KPI updates to keep investigator dashboard synchronized live
                    total_records = db.query(IntelligenceRecord).count()
                    total_evidence = db.query(Evidence).count()
                    total_alerts = db.query(Alert).filter(Alert.status == "NEW").count()

                    await ws_manager.broadcast({
                        "type": "KPI_TELEMETRY_UPDATE",
                        "metrics": {
                            "total_intelligence_records": total_records,
                            "evidence_items": total_evidence,
                            "unresolved_alerts": total_alerts,
                            "timestamp": datetime.utcnow().isoformat() + "Z"
                        }
                    })

                finally:
                    db.close()

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in realtime crawler daemon: {e}")

            await asyncio.sleep(self.interval_seconds)

realtime_daemon = RealtimeCrawlerDaemon(interval_seconds=5.0)
