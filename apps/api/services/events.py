"""Event tracking service"""
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
import models


def track_event(
    db: Session,
    event_name: str,
    user_id: Optional[str] = None,
    operator_org_id: Optional[str] = None,
    properties: Optional[Dict[str, Any]] = None
):
    """Track an analytics event"""
    event = models.Event(
        event_name=event_name,
        user_id=user_id,
        operator_org_id=operator_org_id,
        properties=properties
    )
    db.add(event)
    db.commit()
    return event
