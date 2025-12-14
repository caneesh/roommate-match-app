from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from database import get_db
import models
from auth import get_current_active_user
from services import track_event, MatchingService

router = APIRouter(prefix="/operator", tags=["operator"])


class PropertyCreateRequest(BaseModel):
    name: str
    address: str
    city: str
    state: str
    zip_code: str


class UnitCreateRequest(BaseModel):
    property_id: str
    unit_number: str


class RoomCreateRequest(BaseModel):
    unit_id: str
    room_number: str
    total_beds: int


class MatchRunRequest(BaseModel):
    property_id: str
    bed_id: Optional[str] = None
    candidate_ids: List[str]
    group_size: int = 2


class MoveInRequest(BaseModel):
    resident_id: str
    bed_id: str
    move_in_date: str


class ConflictReportRequest(BaseModel):
    property_id: str
    unit_id: Optional[str] = None
    category: str
    severity: str
    description: str


def get_operator_org(user: models.User, db: Session):
    """Get operator org for current user"""
    membership = db.query(models.OperatorMember).filter(
        models.OperatorMember.user_id == user.id
    ).first()

    if not membership:
        raise HTTPException(status_code=403, detail="User is not a member of any operator organization")

    return membership.org


@router.get("/dashboard")
def get_dashboard(
    user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get operator dashboard metrics"""
    org = get_operator_org(user, db)

    # Get counts
    properties_count = db.query(models.Property).filter(
        models.Property.operator_org_id == org.id
    ).count()

    # Get applicants count across all properties
    applicants_count = db.query(models.ApplicantPool).join(
        models.Property
    ).filter(
        models.Property.operator_org_id == org.id,
        models.ApplicantPool.status == "pending"
    ).count()

    # Get move-ins count
    move_ins_count = db.query(models.MoveIn).join(
        models.Bed
    ).join(models.Room).join(models.Unit).join(models.Property).filter(
        models.Property.operator_org_id == org.id,
        models.MoveIn.move_out_date.is_(None)
    ).count()

    # Get conflict reports count
    conflicts_count = db.query(models.ConflictReport).join(
        models.Property
    ).filter(
        models.Property.operator_org_id == org.id,
        models.ConflictReport.resolved_at.is_(None)
    ).count()

    # Get recent match runs
    recent_matches = db.query(models.MatchRun).filter(
        models.MatchRun.operator_org_id == org.id
    ).order_by(models.MatchRun.created_at.desc()).limit(5).all()

    return {
        "org_name": org.name,
        "properties_count": properties_count,
        "applicants_count": applicants_count,
        "move_ins_count": move_ins_count,
        "conflicts_count": conflicts_count,
        "recent_match_runs": len(recent_matches)
    }


@router.post("/properties")
def create_property(
    request: PropertyCreateRequest,
    user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    org = get_operator_org(user, db)

    property_obj = models.Property(
        operator_org_id=org.id,
        **request.dict()
    )
    db.add(property_obj)
    db.commit()
    db.refresh(property_obj)

    track_event(db, "property_created", user_id=str(user.id), operator_org_id=str(org.id))

    return {"id": str(property_obj.id), "message": "Property created successfully"}


@router.get("/properties")
def list_properties(
    user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    org = get_operator_org(user, db)

    properties = db.query(models.Property).filter(
        models.Property.operator_org_id == org.id
    ).all()

    return [
        {
            "id": str(p.id),
            "name": p.name,
            "address": p.address,
            "city": p.city,
            "state": p.state,
            "zip_code": p.zip_code,
            "total_units": len(p.units)
        }
        for p in properties
    ]


@router.post("/units")
def create_unit(
    request: UnitCreateRequest,
    user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    org = get_operator_org(user, db)

    # Verify property belongs to org
    property_obj = db.query(models.Property).filter(
        models.Property.id == request.property_id,
        models.Property.operator_org_id == org.id
    ).first()

    if not property_obj:
        raise HTTPException(status_code=404, detail="Property not found")

    unit = models.Unit(**request.dict())
    db.add(unit)
    db.commit()
    db.refresh(unit)

    return {"id": str(unit.id), "message": "Unit created successfully"}


@router.get("/properties/{property_id}/units")
def list_units(
    property_id: str,
    user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    org = get_operator_org(user, db)

    property_obj = db.query(models.Property).filter(
        models.Property.id == property_id,
        models.Property.operator_org_id == org.id
    ).first()

    if not property_obj:
        raise HTTPException(status_code=404, detail="Property not found")

    return [
        {
            "id": str(u.id),
            "unit_number": u.unit_number,
            "total_rooms": len(u.rooms),
            "total_beds": sum(len(r.beds) for r in u.rooms)
        }
        for u in property_obj.units
    ]


@router.post("/rooms")
def create_room(
    request: RoomCreateRequest,
    user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    org = get_operator_org(user, db)

    # Verify unit belongs to org
    unit = db.query(models.Unit).join(models.Property).filter(
        models.Unit.id == request.unit_id,
        models.Property.operator_org_id == org.id
    ).first()

    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")

    room = models.Room(
        unit_id=request.unit_id,
        room_number=request.room_number,
        total_beds=request.total_beds
    )
    db.add(room)
    db.flush()

    # Create beds
    for i in range(request.total_beds):
        bed = models.Bed(
            room_id=room.id,
            bed_number=str(i + 1)
        )
        db.add(bed)

    db.commit()
    db.refresh(room)

    return {"id": str(room.id), "message": "Room created successfully"}


@router.get("/applicants")
def list_applicants(
    property_id: Optional[str] = None,
    user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    org = get_operator_org(user, db)

    query = db.query(models.ApplicantPool).join(
        models.Property
    ).filter(
        models.Property.operator_org_id == org.id
    )

    if property_id:
        query = query.filter(models.ApplicantPool.property_id == property_id)

    applicants = query.all()

    results = []
    for app in applicants:
        resident = app.resident
        user_obj = db.query(models.User).filter(models.User.id == resident.user_id).first()

        results.append({
            "id": str(app.id),
            "resident_id": str(resident.id),
            "resident_name": user_obj.name,
            "resident_email": user_obj.email,
            "property_id": str(app.property_id),
            "status": app.status,
            "questionnaire_completed": resident.questionnaire_completed,
            "applied_at": app.applied_at.isoformat()
        })

    return results


@router.post("/match-runs")
def run_matching(
    request: MatchRunRequest,
    user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    org = get_operator_org(user, db)

    # Verify property belongs to org
    property_obj = db.query(models.Property).filter(
        models.Property.id == request.property_id,
        models.Property.operator_org_id == org.id
    ).first()

    if not property_obj:
        raise HTTPException(status_code=404, detail="Property not found")

    # Create match run
    match_run = models.MatchRun(
        operator_org_id=org.id,
        property_id=request.property_id,
        bed_id=request.bed_id,
        candidate_ids=request.candidate_ids,
        group_size=request.group_size,
        status=models.MatchRunStatus.PENDING,
        created_by=user.id
    )
    db.add(match_run)
    db.commit()
    db.refresh(match_run)

    # Run matching
    try:
        matching_service = MatchingService(db)

        if request.group_size == 2:
            # Pairwise matching for all pairs
            for i, res_a in enumerate(request.candidate_ids):
                for res_b in request.candidate_ids[i+1:]:
                    matching_service.run_pairwise_match(res_a, res_b, str(match_run.id))
        else:
            # Group matching
            matching_service.run_group_match(
                request.candidate_ids,
                request.group_size,
                str(match_run.id)
            )

        match_run.status = models.MatchRunStatus.COMPLETED
        match_run.completed_at = datetime.utcnow()
        db.commit()

        track_event(
            db,
            "match_run_completed",
            user_id=str(user.id),
            operator_org_id=str(org.id),
            properties={"match_run_id": str(match_run.id)}
        )

        return {"id": str(match_run.id), "message": "Matching completed successfully"}

    except Exception as e:
        match_run.status = models.MatchRunStatus.FAILED
        db.commit()
        raise HTTPException(status_code=500, detail=f"Matching failed: {str(e)}")


@router.get("/match-runs/{match_run_id}/results")
def get_match_results(
    match_run_id: str,
    user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    org = get_operator_org(user, db)

    match_run = db.query(models.MatchRun).filter(
        models.MatchRun.id == match_run_id,
        models.MatchRun.operator_org_id == org.id
    ).first()

    if not match_run:
        raise HTTPException(status_code=404, detail="Match run not found")

    results = db.query(models.MatchResult).filter(
        models.MatchResult.match_run_id == match_run_id
    ).order_by(models.MatchResult.compatibility_score.desc()).all()

    formatted_results = []
    for result in results:
        # Get resident names
        resident_a = db.query(models.ResidentProfile).filter(
            models.ResidentProfile.id == result.resident_a_id
        ).first()
        resident_b = db.query(models.ResidentProfile).filter(
            models.ResidentProfile.id == result.resident_b_id
        ).first()

        user_a = db.query(models.User).filter(models.User.id == resident_a.user_id).first()
        user_b = db.query(models.User).filter(models.User.id == resident_b.user_id).first()

        formatted_results.append({
            "id": str(result.id),
            "resident_a": {
                "id": str(resident_a.id),
                "name": user_a.name,
                "email": user_a.email
            },
            "resident_b": {
                "id": str(resident_b.id),
                "name": user_b.name,
                "email": user_b.email
            },
            "compatibility_score": result.compatibility_score,
            "risk_level": result.risk_level,
            "category_scores": result.category_scores,
            "top_alignments": result.top_alignments,
            "top_mismatches": result.top_mismatches,
            "mitigation_tips": result.mitigation_tips,
            "recommended_house_rules": result.recommended_house_rules
        })

    track_event(
        db,
        "match_report_viewed",
        user_id=str(user.id),
        operator_org_id=str(org.id)
    )

    return formatted_results


@router.post("/move-ins")
def create_move_in(
    request: MoveInRequest,
    user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    org = get_operator_org(user, db)

    # Verify bed belongs to org
    bed = db.query(models.Bed).join(
        models.Room
    ).join(models.Unit).join(models.Property).filter(
        models.Bed.id == request.bed_id,
        models.Property.operator_org_id == org.id
    ).first()

    if not bed:
        raise HTTPException(status_code=404, detail="Bed not found")

    move_in = models.MoveIn(
        resident_id=request.resident_id,
        bed_id=request.bed_id,
        move_in_date=datetime.fromisoformat(request.move_in_date)
    )
    db.add(move_in)

    # Mark bed as occupied
    bed.is_occupied = True
    bed.current_resident_id = request.resident_id

    db.commit()

    track_event(db, "move_in_created", user_id=str(user.id), operator_org_id=str(org.id))

    return {"message": "Move-in recorded successfully"}


@router.post("/conflict-reports")
def create_conflict_report(
    request: ConflictReportRequest,
    user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    org = get_operator_org(user, db)

    # Verify property belongs to org
    property_obj = db.query(models.Property).filter(
        models.Property.id == request.property_id,
        models.Property.operator_org_id == org.id
    ).first()

    if not property_obj:
        raise HTTPException(status_code=404, detail="Property not found")

    report = models.ConflictReport(
        reported_by=user.id,
        **request.dict()
    )
    db.add(report)
    db.commit()

    track_event(
        db,
        "conflict_reported",
        user_id=str(user.id),
        operator_org_id=str(org.id),
        properties={"category": request.category, "severity": request.severity}
    )

    return {"message": "Conflict report submitted successfully"}


@router.get("/conflict-reports")
def list_conflict_reports(
    user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    org = get_operator_org(user, db)

    reports = db.query(models.ConflictReport).join(
        models.Property
    ).filter(
        models.Property.operator_org_id == org.id
    ).order_by(models.ConflictReport.created_at.desc()).all()

    return [
        {
            "id": str(r.id),
            "property_id": str(r.property_id),
            "category": r.category,
            "severity": r.severity,
            "description": r.description,
            "resolved": r.resolved_at is not None,
            "created_at": r.created_at.isoformat()
        }
        for r in reports
    ]
