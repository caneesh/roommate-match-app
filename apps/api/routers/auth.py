from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from database import get_db
import models
from auth import get_password_hash, verify_password, create_access_token
from services import track_event

router = APIRouter(prefix="/auth", tags=["auth"])


class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    name: str
    role: str = "resident"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict


@router.post("/signup", response_model=TokenResponse)
def signup(request: SignupRequest, db: Session = Depends(get_db)):
    # Check if user exists
    existing = db.query(models.User).filter(models.User.email == request.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create user
    user = models.User(
        email=request.email,
        hashed_password=get_password_hash(request.password),
        name=request.name,
        role=request.role
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Create resident profile if role is resident
    if request.role == "resident":
        profile = models.ResidentProfile(user_id=user.id)
        db.add(profile)
        db.commit()

    # Track event
    track_event(db, "signup", user_id=str(user.id), properties={"role": request.role})

    # Create token
    access_token = create_access_token(data={"sub": str(user.id)})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": str(user.id),
            "email": user.email,
            "name": user.name,
            "role": user.role
        }
    }


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == request.email).first()

    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    if not user.is_active:
        raise HTTPException(status_code=400, detail="User account is inactive")

    # Track event
    track_event(db, "login", user_id=str(user.id))

    access_token = create_access_token(data={"sub": str(user.id)})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": str(user.id),
            "email": user.email,
            "name": user.name,
            "role": user.role
        }
    }


@router.get("/verify")
def verify_token(db: Session = Depends(get_db)):
    """Verify token and return user info"""
    # Import here to avoid circular dependency
    from auth import get_current_active_user

    # This endpoint is currently not used, but kept for future compatibility
    return {"message": "Use the token in Authorization header for authentication"}

