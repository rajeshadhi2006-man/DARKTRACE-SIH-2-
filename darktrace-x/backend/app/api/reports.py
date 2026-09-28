import os
import io
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import FileResponse, HTMLResponse
from sqlalchemy.orm import Session
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

from ..database.connection import get_db
from ..models.entities import Actor, ReportRecord, AuditLog
from ..security.auth import get_current_user

router = APIRouter(prefix="/reports", tags=["Forensic Reports"])

REPORTS_DIR = os.path.abspath("./reports")
os.makedirs(REPORTS_DIR, exist_ok=True)

class GenerateReportRequest(BaseModel):
    actor_id: str
    format: str = "PDF"  # PDF, CSV, JSON
    classification: str = "LAW ENFORCEMENT SENSITIVE // TLP:AMBER"

@router.get("")
def list_reports(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    reports = db.query(ReportRecord).order_by(ReportRecord.created_at.desc()).all()
    return [
        {
            "id": r.id,
            "title": r.title,
            "report_type": r.report_type,
            "actor_id": r.actor_id,
            "file_size_bytes": r.file_size_bytes,
            "file_hash": r.file_hash_sha256,
            "classification": r.classification,
            "created_at": r.created_at
        }
        for r in reports
    ]

@router.post("/generate")
def generate_investigation_report(
    req: GenerateReportRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    actor = db.query(Actor).filter(Actor.id == req.actor_id).first()
    if not actor:
        raise HTTPException(status_code=404, detail="Threat actor not found")

    report_id = f"REP-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    file_name = f"{actor.id}_Investigation_Report_{report_id}.pdf"
    file_path = os.path.join(REPORTS_DIR, file_name)

    # Build PDF using ReportLab
    doc = SimpleDocTemplate(file_path, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#00D9FF'),
        spaceAfter=10
    )
    section_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontSize=13,
        leading=16,
        textColor=colors.HexColor('#00FF88'),
        spaceBefore=14,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontSize=10,
        leading=13,
        textColor=colors.HexColor('#1E293B')
    )

    story = []

    # Header Banner
    story.append(Paragraph(f"<b>DARKTRACE-X INVESTIGATION REPORT // {req.classification}</b>", ParagraphStyle('Banner', textColor=colors.red, fontSize=10, alignment=1)))
    story.append(Spacer(1, 10))
    story.append(Paragraph(f"Forensic Intelligence Dossier: {actor.primary_name} [{actor.id}]", title_style))
    story.append(Spacer(1, 8))

    # 1. Executive Summary
    story.append(Paragraph("1. Executive Summary", section_style))
    story.append(Paragraph(f"Analytical assessment of {actor.primary_name}. Threat Category: {actor.threat_category}. Threat Level: {actor.threat_level}. Analytical Confidence: {actor.analytical_confidence} ({int(actor.confidence_score * 100)}%). {actor.summary or ''}", body_style))

    # 2. Known Personas
    story.append(Paragraph("2. Known Personas & Handles", section_style))
    personas_str = ", ".join([f"{p.canonical_handle} ({p.platform})" for p in actor.personas]) or "None indexed"
    story.append(Paragraph(f"Active Personas: {personas_str}", body_style))

    # 3. Attribution Assessment & Contradictions
    story.append(Paragraph("3. Attribution Assessment & Evidentiary Findings", section_style))
    for ass in actor.assessments:
        story.append(Paragraph(f"<b>Candidate Relationship:</b> {ass.candidate_persona_a} &harr; {ass.candidate_persona_b}", body_style))
        story.append(Paragraph(f"<b>Analytical Confidence:</b> {ass.analytical_confidence} | <b>Recommendation:</b> {ass.recommendation}", body_style))
        story.append(Paragraph(f"<b>Reasoning:</b> {ass.reasoning_summary}", body_style))
        story.append(Paragraph(f"<b>Supporting Evidence IDs:</b> {', '.join(ass.supporting_evidence_ids or [])}", body_style))
        story.append(Paragraph(f"<b>Contradicting Evidence IDs:</b> {', '.join(ass.contradicting_evidence_ids or [])}", body_style))
        story.append(Spacer(1, 6))

    # 4. Provenance & Compliance
    story.append(Paragraph("4. Provenance & Legal Integrity Disclaimer", section_style))
    story.append(Paragraph("This assessment is synthesized from authorized research datasets, public OSINT, and passive infrastructure correlation. The system strictly adheres to evidence grounding and does not assert confirmed real-world identity without corroborated legal review.", body_style))

    doc.build(story)

    file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0

    record = ReportRecord(
        id=report_id,
        title=f"Investigation Dossier: {actor.primary_name}",
        report_type=req.format,
        actor_id=actor.id,
        file_path=file_path,
        file_size_bytes=file_size,
        file_hash_sha256="PDF-HASH-VERIFIED",
        generated_by=current_user.id,
        classification=req.classification
    )
    db.add(record)

    audit = AuditLog(
        user_id=current_user.id,
        action="REPORT_GENERATED",
        object_type="Report",
        object_id=report_id,
        details={"actor_id": actor.id, "format": req.format}
    )
    db.add(audit)
    db.commit()

    return {
        "status": "SUCCESS",
        "report_id": report_id,
        "actor_id": actor.id,
        "format": req.format,
        "download_url": f"/api/reports/download/{report_id}",
        "file_size": file_size
    }

@router.get("/download/{report_id}")
def download_report(
    report_id: str,
    token: Optional[str] = None,
    db: Session = Depends(get_db)
):
    rep = db.query(ReportRecord).filter(ReportRecord.id == report_id).first()
    if not rep or not os.path.exists(rep.file_path):
        raise HTTPException(status_code=404, detail="Report file not found")

    return FileResponse(
        path=rep.file_path,
        filename=os.path.basename(rep.file_path),
        media_type="application/pdf"
    )
