import json
import csv
import io
import hashlib
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from ..database.connection import get_db
from ..models.entities import IntelligenceRecord, Source, AuditLog
from ..security.auth import get_current_user

router = APIRouter(prefix="/intelligence", tags=["Intelligence & Ingestion"])

@router.get("")
def list_intelligence(
    source_id: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    q = db.query(IntelligenceRecord)
    if source_id:
        q = q.filter(IntelligenceRecord.source_id == source_id)
    records = q.order_by(IntelligenceRecord.timestamp.desc()).limit(limit).all()

    return [
        {
            "id": r.id,
            "source_id": r.source_id,
            "record_type": r.record_type,
            "author_raw": r.author_raw,
            "content_preview": r.content_raw[:120] + "..." if len(r.content_raw) > 120 else r.content_raw,
            "content_hash": r.content_sha256,
            "timestamp": r.timestamp,
            "confidence": r.confidence,
            "reliability": r.reliability,
            "provenance": r.provenance
        }
        for r in records
    ]

@router.post("/upload")
async def upload_intelligence_dataset(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Ingests intelligence datasets in CSV or JSON format.
    Workflow: UPLOAD -> VALIDATE -> PARSE -> NORMALIZE -> ENTITY EXTRACTION -> STORE -> AUDIT.
    """
    filename = file.filename.lower()
    if not (filename.endswith(".csv") or filename.endswith(".json")):
        raise HTTPException(status_code=400, detail="Invalid file type. Only CSV and JSON datasets supported.")

    content = await file.read()
    if len(content) > 50 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File exceeds 50MB limit.")

    extracted_records = 0
    now = datetime.utcnow()

    if filename.endswith(".json"):
        try:
            data = json.loads(content.decode("utf-8"))
            if not isinstance(data, list):
                data = [data]
            for item in data:
                text_content = item.get("content", item.get("text", json.dumps(item)))
                h = hashlib.sha256(text_content.encode()).hexdigest()
                rec = IntelligenceRecord(
                    id=f"OBS-{datetime.utcnow().strftime('%M%S%f')[:8]}",
                    source_id=item.get("source_id", "SRC-UPLOAD"),
                    record_type=item.get("type", "UPLOADED_INTEL"),
                    author_raw=item.get("author", "unknown_source"),
                    content_raw=text_content,
                    content_sha256=h,
                    timestamp=now,
                    confidence=0.85,
                    reliability="B",
                    provenance=f"Uploaded file: {file.filename} by {current_user.username}"
                )
                db.add(rec)
                extracted_records += 1
            db.commit()
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"JSON parse error: {e}")

    elif filename.endswith(".csv"):
        try:
            csv_text = content.decode("utf-8")
            reader = csv.DictReader(io.StringIO(csv_text))
            for row in reader:
                text_content = row.get("content", row.get("text", json.dumps(row)))
                h = hashlib.sha256(text_content.encode()).hexdigest()
                rec = IntelligenceRecord(
                    id=f"OBS-{datetime.utcnow().strftime('%M%S%f')[:8]}",
                    source_id=row.get("source_id", "SRC-UPLOAD"),
                    record_type=row.get("type", "UPLOADED_INTEL"),
                    author_raw=row.get("author", "unknown_source"),
                    content_raw=text_content,
                    content_sha256=h,
                    timestamp=now,
                    confidence=0.85,
                    reliability="B",
                    provenance=f"Uploaded CSV: {file.filename} by {current_user.username}"
                )
                db.add(rec)
                extracted_records += 1
            db.commit()
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"CSV parse error: {e}")

    # Audit log
    audit = AuditLog(
        user_id=current_user.id,
        action="DATASET_INGESTION",
        object_type="File",
        object_id=file.filename,
        details={"records_ingested": extracted_records, "file_size": len(content)}
    )
    db.add(audit)
    db.commit()

    return {
        "status": "INGESTION_COMPLETED",
        "filename": file.filename,
        "records_ingested": extracted_records,
        "workflow": "UPLOAD -> VALIDATE -> PARSE -> NORMALIZE -> EXTRACT -> STORE",
        "timestamp": now
    }

from ..services.ingestion.collector import autonomous_collector
from pydantic import BaseModel
import uuid
from ..models.entities import Evidence, Alert

class CustomInterceptRequest(BaseModel):
    source_name: str
    author: str
    raw_text: str
    category: Optional[str] = "Live Analyst Intercept"

@router.post("/crawl")
def trigger_autonomous_crawl(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Triggers an autonomous dark web crawler sweep across Dread, BreachForums,
    and underground marketplaces, extracting crypto wallets and PGP indicators.
    """
    result = autonomous_collector.trigger_crawler_cycle(db, user_id=current_user.id)
    return result

@router.post("/inject")
def inject_custom_intercept(
    req: CustomInterceptRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Analyst Real-Time Threat Hunting & Intercept Injection:
    Ingests analyst-supplied darknet post or chat log, extracts cryptographic/network indicators,
    calculates SHA-256 hash, creates Evidence, logs audit trail, and broadcasts over WebSocket in real time.
    """
    now = datetime.utcnow()
    content_hash = hashlib.sha256(req.raw_text.encode("utf-8")).hexdigest()
    uid = uuid.uuid4().hex[:6].upper()

    rec_id = f"OBS-ANALYST-{now.strftime('%H%M%S')}-{uid}"
    record = IntelligenceRecord(
        id=rec_id,
        source_id="SRC-CUSTOM",
        record_type="ANALYST_LIVE_INJECTION",
        author_raw=req.author,
        content_raw=req.raw_text,
        content_sha256=content_hash,
        timestamp=now,
        confidence=0.95,
        reliability="A",
        provenance=f"Analyst Terminal ({current_user.username}) -> {req.source_name}"
    )
    db.add(record)

    # Extract indicators using autonomous_collector
    extracted = autonomous_collector.extract_indicators(req.raw_text)

    # Evidence record
    evid_id = f"EVID-LIVE-{now.strftime('%H%M%S')}-{uid}"
    evid = Evidence(
        id=evid_id,
        source_id="SRC-CUSTOM",
        observation_id=rec_id,
        evidence_type="IDENTITY",
        title=f"Analyst Intercept: {req.author} on {req.source_name}",
        description=req.raw_text,
        content_hash=content_hash,
        confidence=0.95,
        reliability="A",
        related_entity_ids=[rec_id],
        provenance=f"Analyst Terminal (Operator: {current_user.username}) -> {req.source_name}"
    )
    db.add(evid)

    # Alert if high-risk indicators or terms
    if any(k in req.raw_text.lower() for k in ["0day", "exploit", "leak", "breach", "ransom", "xmr", "btc"]):
        alt_id = f"ALT-LIVE-{now.strftime('%H%M%S')}-{uid}"
        alt = Alert(
            id=alt_id,
            title=f"Live Flagged Intercept: {req.author} on {req.source_name}",
            event_type="ANALYST_INTERCEPT_FLAG",
            severity="HIGH",
            confidence=0.92,
            description=f"Analyst intercepted live darknet message on {req.source_name}. Extracted {len(extracted.get('btc_wallets', []))} BTC, {len(extracted.get('xmr_wallets', []))} XMR, {len(extracted.get('onion_services', []))} Onions, {len(extracted.get('clearnet_ips', []))} Clearnet IPs.",
            supporting_evidence_count=1,
            status="NEW"
        )
        db.add(alt)

    db.commit()

    res = {
        "status": "LIVE_INTERCEPT_INJECTED",
        "record_id": rec_id,
        "evidence_id": evid_id,
        "source": req.source_name,
        "author": req.author,
        "content_hash": content_hash,
        "extracted_indicators": extracted,
        "timestamp": now.isoformat() + "Z"
    }

    # Broadcast over WebSocket
    try:
        from ..services.realtime.manager import ws_manager
        ws_manager.broadcast_sync({
            "type": "NEW_DARKNET_INTERCEPT",
            "event_title": f"Live Analyst Intercept: {req.author} on {req.source_name}",
            "source": req.source_name,
            "author": req.author,
            "data": res,
            "timestamp": now.isoformat() + "Z"
        })

        total_records = db.query(IntelligenceRecord).count()
        total_evidence = db.query(Evidence).count()
        total_alerts = db.query(Alert).filter(Alert.status == "NEW").count()

        ws_manager.broadcast_sync({
            "type": "KPI_TELEMETRY_UPDATE",
            "metrics": {
                "total_intelligence_records": total_records,
                "evidence_items": total_evidence,
                "unresolved_alerts": total_alerts,
                "timestamp": now.isoformat() + "Z"
            }
        })
    except Exception:
        pass

    return res


