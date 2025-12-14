from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from database import get_db
import models
from auth import get_current_active_user, require_role
from services import track_event

router = APIRouter(prefix="/resident", tags=["resident"])


class QuestionnaireRequest(BaseModel):
    sleep_schedule_weekday: int
    sleep_schedule_weekend: int
    light_sensitivity: int
    noise_tolerance: int
    quiet_hours_importance: int
    cleanliness_kitchen: int
    cleanliness_bathroom: int
    cleanliness_common: int
    chore_frequency: int
    clutter_tolerance: int
    guests_overnight_per_week: int
    partner_frequency: int
    party_frequency: int
    social_level_home: int
    introvert_extrovert: int
    thermostat_preference: int
    thermostat_flexibility: int
    wfh_frequency: int
    shared_space_work_need: int
    food_sharing_comfort: int
    toiletries_sharing_comfort: int
    borrowing_comfort: int
    has_pets: bool
    pet_types: Optional[List[str]] = None
    has_allergies: bool
    allergy_details: Optional[List[str]] = None
    smoking_tolerance: int
    vaping_tolerance: int
    drug_tolerance: int
    alcohol_comfort: int
    communication_directness: int
    communication_channel: str
    response_time_expectation: int
    conflict_style: str
    budget_stress: int
    expense_splitting_preference: str
    spirituality_importance: int
    political_discussion_comfort: int
    sustainability_importance: int
    dealbreakers: List[str]
    flexible_on: List[str]
    pet_peeves: Optional[str] = None
    ideal_roommate_description: Optional[str] = None


class ProfileUpdateRequest(BaseModel):
    phone: Optional[str] = None
    bio: Optional[str] = None


class FeedbackRequest(BaseModel):
    survey_type: str
    satisfaction_score: int
    match_accuracy_score: int
    would_recommend: bool
    feedback_text: Optional[str] = None


@router.get("/profile")
def get_profile(
    user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    profile = db.query(models.ResidentProfile).filter(
        models.ResidentProfile.user_id == user.id
    ).first()

    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    return {
        "id": str(profile.id),
        "phone": profile.phone,
        "bio": profile.bio,
        "profile_complete": profile.profile_complete,
        "questionnaire_completed": profile.questionnaire_completed,
        "has_questionnaire": profile.questionnaire is not None
    }


@router.put("/profile")
def update_profile(
    request: ProfileUpdateRequest,
    user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    profile = db.query(models.ResidentProfile).filter(
        models.ResidentProfile.user_id == user.id
    ).first()

    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    if request.phone is not None:
        profile.phone = request.phone
    if request.bio is not None:
        profile.bio = request.bio

    profile.profile_complete = True
    db.commit()
    db.refresh(profile)

    return {"message": "Profile updated successfully"}


@router.post("/questionnaire")
def submit_questionnaire(
    request: QuestionnaireRequest,
    user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    profile = db.query(models.ResidentProfile).filter(
        models.ResidentProfile.user_id == user.id
    ).first()

    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    # Check if questionnaire exists
    existing = db.query(models.QuestionnaireAnswers).filter(
        models.QuestionnaireAnswers.resident_id == profile.id
    ).first()

    if existing:
        # Update existing
        for key, value in request.dict().items():
            setattr(existing, key.replace('_', '_').lower(), value)
        questionnaire = existing
        track_event(db, "questionnaire_updated", user_id=str(user.id))
    else:
        # Create new
        questionnaire = models.QuestionnaireAnswers(
            resident_id=profile.id,
            **request.dict()
        )
        db.add(questionnaire)
        track_event(db, "questionnaire_completed", user_id=str(user.id))

    profile.questionnaire_completed = True
    db.commit()

    return {"message": "Questionnaire submitted successfully"}


@router.get("/questionnaire")
def get_questionnaire(
    user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    profile = db.query(models.ResidentProfile).filter(
        models.ResidentProfile.user_id == user.id
    ).first()

    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    questionnaire = db.query(models.QuestionnaireAnswers).filter(
        models.QuestionnaireAnswers.resident_id == profile.id
    ).first()

    if not questionnaire:
        raise HTTPException(status_code=404, detail="Questionnaire not found")

    return questionnaire


@router.get("/matches")
def get_matches(
    user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    profile = db.query(models.ResidentProfile).filter(
        models.ResidentProfile.user_id == user.id
    ).first()

    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    # Get matches where user is either resident_a or resident_b
    matches_a = db.query(models.MatchResult).filter(
        models.MatchResult.resident_a_id == profile.id
    ).all()

    matches_b = db.query(models.MatchResult).filter(
        models.MatchResult.resident_b_id == profile.id
    ).all()

    all_matches = matches_a + matches_b

    # Track event
    if all_matches:
        track_event(db, "matches_viewed", user_id=str(user.id))

    results = []
    for match in all_matches:
        # Get the other resident's info
        other_id = match.resident_b_id if match.resident_a_id == profile.id else match.resident_a_id
        other_profile = db.query(models.ResidentProfile).filter(
            models.ResidentProfile.id == other_id
        ).first()
        other_user = db.query(models.User).filter(
            models.User.id == other_profile.user_id
        ).first()

        results.append({
            "id": str(match.id),
            "other_resident": {
                "name": other_user.name,
                "bio": other_profile.bio
            },
            "compatibility_score": match.compatibility_score,
            "risk_score": match.risk_score,
            "risk_level": match.risk_level,
            "category_scores": match.category_scores,
            "category_risks": match.category_risks,
            "top_alignments": match.top_alignments,
            "top_mismatches": match.top_mismatches,
            "mitigation_tips": match.mitigation_tips,
            "recommended_house_rules": match.recommended_house_rules,
            "created_at": match.created_at.isoformat()
        })

    return results


@router.post("/feedback")
def submit_feedback(
    request: FeedbackRequest,
    user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    profile = db.query(models.ResidentProfile).filter(
        models.ResidentProfile.user_id == user.id
    ).first()

    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    feedback = models.FeedbackSurvey(
        resident_id=profile.id,
        **request.dict()
    )
    db.add(feedback)
    db.commit()

    track_event(db, f"feedback_submitted_{request.survey_type}", user_id=str(user.id))

    return {"message": "Feedback submitted successfully"}


@router.delete("/data")
def delete_user_data(
    user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete all user data (GDPR compliance)"""
    profile = db.query(models.ResidentProfile).filter(
        models.ResidentProfile.user_id == user.id
    ).first()

    if profile:
        # Delete questionnaire
        db.query(models.QuestionnaireAnswers).filter(
            models.QuestionnaireAnswers.resident_id == profile.id
        ).delete()

        # Delete profile
        db.query(models.ResidentProfile).filter(
            models.ResidentProfile.id == profile.id
        ).delete()

    # Deactivate user
    user.is_active = False
    db.commit()

    track_event(db, "data_deleted", user_id=str(user.id))

    return {"message": "User data deleted successfully"}
