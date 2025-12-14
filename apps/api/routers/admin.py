from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from database import get_db
import models
from auth import get_current_active_user, require_role

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users")
def list_users(
    user: models.User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    users = db.query(models.User).all()

    return [
        {
            "id": str(u.id),
            "email": u.email,
            "name": u.name,
            "role": u.role,
            "is_active": u.is_active,
            "created_at": u.created_at.isoformat()
        }
        for u in users
    ]


@router.get("/events")
def list_events(
    limit: int = 100,
    user: models.User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    events = db.query(models.Event).order_by(
        desc(models.Event.created_at)
    ).limit(limit).all()

    return [
        {
            "id": str(e.id),
            "event_name": e.event_name,
            "user_id": str(e.user_id) if e.user_id else None,
            "properties": e.properties,
            "created_at": e.created_at.isoformat()
        }
        for e in events
    ]


@router.get("/metrics")
def get_metrics(
    user: models.User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """Get platform-wide metrics"""
    total_users = db.query(models.User).count()
    total_residents = db.query(models.User).filter(
        models.User.role == models.UserRole.RESIDENT
    ).count()
    total_operators = db.query(models.User).filter(
        models.User.role == models.UserRole.OPERATOR
    ).count()

    questionnaires_completed = db.query(models.QuestionnaireAnswers).count()

    match_runs_completed = db.query(models.MatchRun).filter(
        models.MatchRun.status == models.MatchRunStatus.COMPLETED
    ).count()

    total_properties = db.query(models.Property).count()

    conflicts_reported = db.query(models.ConflictReport).count()
    conflicts_unresolved = db.query(models.ConflictReport).filter(
        models.ConflictReport.resolved_at.is_(None)
    ).count()

    return {
        "total_users": total_users,
        "total_residents": total_residents,
        "total_operators": total_operators,
        "questionnaires_completed": questionnaires_completed,
        "match_runs_completed": match_runs_completed,
        "total_properties": total_properties,
        "conflicts_reported": conflicts_reported,
        "conflicts_unresolved": conflicts_unresolved
    }


@router.get("/audit-logs")
def list_audit_logs(
    limit: int = 100,
    user: models.User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    logs = db.query(models.AuditLog).order_by(
        desc(models.AuditLog.created_at)
    ).limit(limit).all()

    return [
        {
            "id": str(log.id),
            "action": log.action,
            "entity_type": log.entity_type,
            "entity_id": str(log.entity_id),
            "user_id": str(log.user_id),
            "changes": log.changes,
            "created_at": log.created_at.isoformat()
        }
        for log in logs
    ]
