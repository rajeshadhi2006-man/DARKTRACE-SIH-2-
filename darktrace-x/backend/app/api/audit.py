from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..database.connection import get_db
from ..models.entities import AuditLog, User
from ..security.auth import get_current_user

router = APIRouter(prefix="/audit", tags=["Audit Logging"])

@router.get("")
def list_audit_logs(
    action: Optional[str] = Query(None),
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    q = db.query(AuditLog)
    if action:
        q = q.filter(AuditLog.action == action)
    
    logs = q.order_by(AuditLog.timestamp.desc()).limit(limit).all()
    results = []
    for l in logs:
        u = db.query(User).filter(User.id == l.user_id).first()
        results.append({
            "id": l.id,
            "user_id": l.user_id,
            "username": u.username if u else "System",
            "action": l.action,
            "object_type": l.object_type,
            "object_id": l.object_id,
            "details": l.details,
            "ip_address": l.ip_address,
            "timestamp": l.timestamp
        })
    return results
