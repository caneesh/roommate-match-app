from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional
from database import get_db
import models
from services import track_event

router = APIRouter(prefix="/public", tags=["public"])


class LeadRequest(BaseModel):
    org_name: str
    contact_name: str
    contact_email: EmailStr
    contact_phone: Optional[str] = None
    property_count: Optional[int] = None
    unit_count: Optional[int] = None
    message: Optional[str] = None


@router.post("/leads")
def submit_lead(request: LeadRequest, db: Session = Depends(get_db)):
    """Submit a pilot program request"""
    lead = models.Lead(**request.dict())
    db.add(lead)
    db.commit()

    track_event(
        db,
        "pilot_request_submitted",
        properties={"org_name": request.org_name}
    )

    return {"message": "Thank you for your interest! We'll be in touch soon."}


@router.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
