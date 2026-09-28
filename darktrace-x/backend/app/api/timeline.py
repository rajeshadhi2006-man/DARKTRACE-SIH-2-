from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database.connection import get_db
from ..models.entities import TimelineEvent
from ..schemas.entities import TimelineEventResponse
from ..security.auth import get_current_user

router = APIRouter(prefix="/timeline", tags=["Investigation Timeline"])

@router.get("/{actor_id}", response_model=List[TimelineEventResponse])
def get_actor_timeline(
    actor_id: str,
    event_type: Optional[str] = Query(None),
    source_id: Optional[str] = Query(None),
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    q = db.query(TimelineEvent).filter(TimelineEvent.actor_id == actor_id)
    if event_type:
        q = q.filter(TimelineEvent.event_type == event_type)
    if source_id:
        q = q.filter(TimelineEvent.source_id == source_id)

    events = q.order_by(TimelineEvent.event_timestamp.desc()).limit(limit).all()
    results = []
    for e in events:
        results.append(TimelineEventResponse(
            id=e.id,
            actor_id=e.actor_id,
            persona_id=e.persona_id,
            event_type=e.event_type,
            title=e.title,
            description=e.description,
            event_timestamp=e.event_timestamp,
            source_id=e.source_id,
            evidence_id=e.evidence_id,
            confidence=e.confidence
        ))
    return results
