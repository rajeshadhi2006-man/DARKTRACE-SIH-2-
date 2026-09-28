import os
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .database.connection import (
    engine, Base, SessionLocal,
    check_db_health, check_neo4j_health, check_redis_health
)
from .security.auth import seed_default_roles_and_users
from .database.seed_data import seed_complete_synthetic_intelligence

# Import API Routers
from .api.auth import router as auth_router
from .api.dashboard import router as dashboard_router
from .api.actors import router as actors_router
from .api.personas import router as personas_router
from .api.intelligence import router as intelligence_router
from .api.evidence import router as evidence_router
from .api.graph import router as graph_router
from .api.timeline import router as timeline_router
from .api.attribution import router as attribution_router
from .api.analytics import router as analytics_router
from .api.reports import router as reports_router
from .api.search import router as search_router
from .api.audit import router as audit_router
from .api.investigations import router as investigations_router
from .api.campaigns import router as campaigns_router
from .api.alerts import router as alerts_router
from .api.stix import router as stix_router
from .api.mitre import router as mitre_router
from .api.realtime import router as realtime_router
from .api.network_detection import router as network_detection_router
from .api.supabase import router as supabase_router
from .api.analysis import router as analysis_router
from .api.infrastructure import router as infrastructure_router
from .services.supabase_service import check_supabase_health
from .services.realtime.crawler_daemon import realtime_daemon

# Initialize FastAPI App
app = FastAPI(
    title="DARKTRACE-X API",
    description="AI-Powered Dark Web Threat Intelligence, Entity Resolution & Attribution Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:8000",
    "http://localhost:8000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------- Startup & Shutdown Events -----------------
@app.on_event("startup")
async def on_startup():
    # 1. Create database schema
    Base.metadata.create_all(bind=engine)
    
    # 2. Seed system roles and auth users (clean zero data state)
    db = SessionLocal()
    try:
        seed_default_roles_and_users(db)
    finally:
        db.close()

    import asyncio
    ws_manager.set_loop(asyncio.get_running_loop())

    # 3. Launch Real-Time Darknet Telemetry Daemon
    realtime_daemon.start()

@app.on_event("shutdown")
def on_shutdown():
    realtime_daemon.stop()

# ----------------- Health Check Endpoints -----------------
@app.get("/api/health", tags=["System Health"])
def health_check():
    """Returns real-time health status of PostgreSQL/SQLite, Neo4j, and Redis."""
    db_health = check_db_health()
    neo_health = check_neo4j_health()
    redis_health = check_redis_health()
    supabase_health = check_supabase_health()

    is_overall_healthy = (db_health.get("status") == "HEALTHY")

    return {
        "status": "HEALTHY" if is_overall_healthy else "DEGRADED",
        "service": "DARKTRACE-X",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "version": "1.0.0",
        "components": {
            "relational_database": db_health,
            "graph_database": neo_health,
            "cache_broker": redis_health,
            "supabase_cloud": supabase_health
        }
    }

@app.get("/api/status", tags=["System Health"])
def system_status():
    return {
        "platform": "DARKTRACE-X Cyber Threat Intelligence",
        "mode": "AUTHORIZED_CTI_RESEARCH",
        "environment": os.getenv("APP_ENV", "development"),
        "compliance": "Evidence-grounded attribution // Passive telemetry only",
        "supabase": check_supabase_health().get("status", "STANDBY"),
        "time_utc": datetime.utcnow().isoformat() + "Z"
    }

# ----------------- Include API Routers -----------------
app.include_router(auth_router, prefix="/api")
app.include_router(dashboard_router, prefix="/api")
app.include_router(actors_router, prefix="/api")
app.include_router(personas_router, prefix="/api")
app.include_router(intelligence_router, prefix="/api")
app.include_router(evidence_router, prefix="/api")
app.include_router(graph_router, prefix="/api")
app.include_router(timeline_router, prefix="/api")
app.include_router(attribution_router, prefix="/api")
app.include_router(analytics_router, prefix="/api")
app.include_router(reports_router, prefix="/api")
app.include_router(search_router, prefix="/api")
app.include_router(audit_router, prefix="/api")
app.include_router(investigations_router, prefix="/api")
app.include_router(campaigns_router, prefix="/api")
app.include_router(alerts_router, prefix="/api")
app.include_router(stix_router, prefix="/api")
app.include_router(mitre_router, prefix="/api")
app.include_router(realtime_router, prefix="/api")
app.include_router(network_detection_router, prefix="/api")
app.include_router(supabase_router, prefix="/api")
app.include_router(analysis_router, prefix="/api")
app.include_router(infrastructure_router, prefix="/api")

# ----------------- Real-Time WebSocket Telemetry Endpoint -----------------
from fastapi import WebSocket, WebSocketDisconnect
from .services.realtime.manager import ws_manager

@app.websocket("/api/ws/telemetry")
async def websocket_telemetry_endpoint(websocket: WebSocket):
    """
    Real-Time WebSocket Feed:
    Streams live dark web intercepts, crawler cycles, and KPI updates to connected investigator consoles.
    """
    await ws_manager.connect(websocket)
    try:
        await websocket.send_json({
            "type": "CONNECTION_ESTABLISHED",
            "service": "DARKTRACE-X REAL-TIME TELEMETRY FEED",
            "status": "STREAMING_LIVE",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        })
        while True:
            client_msg = await websocket.receive_text()
            await websocket.send_json({
                "type": "PONG",
                "received": client_msg,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            })
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception:
        ws_manager.disconnect(websocket)


from fastapi.responses import FileResponse

# Static mounting for frontend assets and SPA client-side routing
FRONTEND_DIST = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist"))
if os.path.exists(FRONTEND_DIST):
    assets_dir = os.path.join(FRONTEND_DIST, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="frontend-assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa_frontend(full_path: str):
        # Check if requesting an existing file in dist (e.g., favicon.ico, robots.txt)
        file_path = os.path.join(FRONTEND_DIST, full_path)
        if full_path and os.path.isfile(file_path):
            return FileResponse(file_path)
        # Fallback to index.html for client-side React Router navigation
        index_path = os.path.join(FRONTEND_DIST, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        return {"detail": "Frontend build not found"}
