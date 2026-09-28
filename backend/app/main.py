import os
from typing import Optional, List
from fastapi import FastAPI, HTTPException, Query, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse

from .models import (
    StylometryAnalysisRequest,
    OnionScanRequest
)
from .database import db
from .services.graph_engine import graph_engine
from .services.stylometry_engine import stylometry_engine
from .services.tor_recon import tor_recon_engine
from .services.autonomous_crawler import AutonomousDarkWebCollector
from .services.report_generator import ThreatIntelReportGenerator

app = FastAPI(
    title="Dark Web Threat Actor De-Anonymization Platform",
    description="Intelligence attribution engine unmasking Tor hidden service operators, mapping underground relationships, and profiling stylometric personas.",
    version="1.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

crawler = AutonomousDarkWebCollector(db)

# ----------------- REST API Endpoints -----------------

@app.get("/api/stats")
def get_stats():
    """Returns overview statistics of the intelligence platform."""
    return db.get_summary_stats()

@app.get("/api/actors")
def get_actors(
    category: Optional[str] = Query(None, description="Filter by category"),
    source: Optional[str] = Query(None, description="Filter by source marketplace or forum"),
    min_confidence: Optional[int] = Query(None, ge=0, le=100, description="Minimum confidence percentage"),
    query: Optional[str] = Query(None, description="Search term for handles, wallets, PGP, or text"),
    start_date: Optional[str] = Query(None, description="Filter start date YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="Filter end date YYYY-MM-DD")
):
    """Queries threat actor database across a timeline and custom search filters."""
    return db.get_all_actors(
        category=category,
        source=source,
        min_confidence=min_confidence,
        query=query,
        start_date=start_date,
        end_date=end_date
    )

@app.get("/api/actors/{actor_id}")
def get_actor_detail(actor_id: str):
    """Retrieves comprehensive threat actor dossier."""
    actor = db.get_actor_by_id(actor_id)
    if not actor:
        raise HTTPException(status_code=404, detail="Threat actor not found")
    return actor

@app.get("/api/graph")
def get_relationship_graph(actor_id: Optional[str] = Query(None, description="Focus on specific actor neighborhood")):
    """Returns cross-marketplace relationship graph nodes and edges for visualization."""
    return graph_engine.export_graph_for_visualization(actor_filter=actor_id)

@app.get("/api/graph/path")
def get_attribution_path(from_node: str, to_node: str):
    """Computes shortest evidentiary path between two entities in the graph."""
    path = graph_engine.find_shortest_attribution_path(from_node, to_node)
    if path is None:
        raise HTTPException(status_code=404, detail="No connected attribution path found")
    return {"path": path}

@app.post("/api/stylometry/analyze")
def analyze_stylometry(req: StylometryAnalysisRequest):
    """
    AI Stylometric Persona Identification:
    Calculates syntactic writeprints, vocabulary richness, punctuation patterns,
    and matches against indexed darkweb actor corpora.
    """
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    features = stylometry_engine.extract_writeprint(req.text)
    matches = stylometry_engine.match_unknown_post(req.text)
    
    return {
        "text_sample_preview": req.text[:120] + "..." if len(req.text) > 120 else req.text,
        "features": features,
        "candidate_matches": matches
    }

@app.get("/api/recon/targets")
def get_recon_targets():
    """Lists all monitored Tor hidden services with identified misconfigurations."""
    return tor_recon_engine.list_all_recon_targets()

@app.post("/api/recon/scan")
def scan_onion_infrastructure(req: OnionScanRequest):
    """
    Executes deep misconfiguration analysis against a Tor hidden service:
    Checks /server-status, TLS Certificate SAN leaks, Favicon MurmurHash3,
    and correlates with clearnet origin hosting IP.
    """
    if not req.onion_url.strip():
        raise HTTPException(status_code=400, detail="Onion address is required")
    
    result = tor_recon_engine.scan_onion_service(req.onion_url)
    return result

@app.get("/api/telemetry/feed")
def get_telemetry_feed():
    """Returns latest real-time dark web forum and sensor telemetry."""
    return db.live_telemetry_feed

@app.post("/api/crawler/trigger")
def trigger_crawler_round():
    """Manually triggers an autonomous ingestion cycle from dark web sources."""
    result = crawler.trigger_crawl_cycle()
    return result

# ----------------- Export Endpoints -----------------

@app.get("/api/export/csv")
def export_actors_csv():
    """Exports indexed threat actors in CSV format."""
    actors = list(db.actors.values())
    csv_data = ThreatIntelReportGenerator.generate_csv(actors)
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=darkweb_threat_intel_export.csv"}
    )

@app.get("/api/export/json")
def export_actors_json():
    """Exports indexed threat actors in structured JSON format."""
    actors = list(db.actors.values())
    return JSONResponse(
        content=actors,
        headers={"Content-Disposition": "attachment; filename=darkweb_threat_intel_export.json"}
    )

@app.get("/api/export/report/{actor_id}", response_class=HTMLResponse)
def export_forensic_report(actor_id: str):
    """Generates an official law enforcement forensic dossier HTML report."""
    actor = db.get_actor_by_id(actor_id)
    if not actor:
        raise HTTPException(status_code=404, detail="Threat actor not found")
    html_report = ThreatIntelReportGenerator.generate_forensic_html_report(actor)
    return HTMLResponse(content=html_report)

# ----------------- Frontend Static Files -----------------
FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend"))

if os.path.exists(FRONTEND_DIR):
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
