from sqlalchemy import Boolean, Column, String, Integer, Float, DateTime, ForeignKey, JSON, Text, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import uuid
import enum


class UserRole(str, enum.Enum):
    RESIDENT = "resident"
    OPERATOR = "operator"
    ADMIN = "admin"


class RiskLevel(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class MatchRunStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    name = Column(String, nullable=False)
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.RESIDENT)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    resident_profile = relationship("ResidentProfile", back_populates="user", uselist=False)
    operator_memberships = relationship("OperatorMember", back_populates="user")
    created_match_runs = relationship("MatchRun", back_populates="creator", foreign_keys="MatchRun.created_by")


class ResidentProfile(Base):
    __tablename__ = "resident_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False)
    phone = Column(String)
    bio = Column(Text)
    profile_complete = Column(Boolean, default=False)
    questionnaire_completed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="resident_profile")
    questionnaire = relationship("QuestionnaireAnswers", back_populates="resident", uselist=False)
    applicant_pools = relationship("ApplicantPool", back_populates="resident")
    match_results_a = relationship("MatchResult", back_populates="resident_a", foreign_keys="MatchResult.resident_a_id")
    match_results_b = relationship("MatchResult", back_populates="resident_b", foreign_keys="MatchResult.resident_b_id")
    move_ins = relationship("MoveIn", back_populates="resident")
    feedback_surveys = relationship("FeedbackSurvey", back_populates="resident")


class QuestionnaireAnswers(Base):
    __tablename__ = "questionnaire_answers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resident_id = Column(UUID(as_uuid=True), ForeignKey("resident_profiles.id"), unique=True, nullable=False)

    # Sleep & Noise
    sleep_schedule_weekday = Column(Integer, nullable=False)  # 0-10
    sleep_schedule_weekend = Column(Integer, nullable=False)
    light_sensitivity = Column(Integer, nullable=False)
    noise_tolerance = Column(Integer, nullable=False)
    quiet_hours_importance = Column(Integer, nullable=False)

    # Cleanliness
    cleanliness_kitchen = Column(Integer, nullable=False)
    cleanliness_bathroom = Column(Integer, nullable=False)
    cleanliness_common = Column(Integer, nullable=False)
    chore_frequency = Column(Integer, nullable=False)  # times per week
    clutter_tolerance = Column(Integer, nullable=False)

    # Guests & Social
    guests_overnight_per_week = Column(Integer, nullable=False)
    partner_frequency = Column(Integer, nullable=False)
    party_frequency = Column(Integer, nullable=False)
    social_level_home = Column(Integer, nullable=False)
    introvert_extrovert = Column(Integer, nullable=False)

    # Environment
    thermostat_preference = Column(Integer, nullable=False)  # degrees F
    thermostat_flexibility = Column(Integer, nullable=False)
    wfh_frequency = Column(Integer, nullable=False)  # days per week
    shared_space_work_need = Column(Integer, nullable=False)

    # Sharing
    food_sharing_comfort = Column(Integer, nullable=False)
    toiletries_sharing_comfort = Column(Integer, nullable=False)
    borrowing_comfort = Column(Integer, nullable=False)

    # Pets & Lifestyle
    has_pets = Column(Boolean, nullable=False)
    pet_types = Column(ARRAY(String), nullable=True)
    has_allergies = Column(Boolean, nullable=False)
    allergy_details = Column(ARRAY(String), nullable=True)
    smoking_tolerance = Column(Integer, nullable=False)
    vaping_tolerance = Column(Integer, nullable=False)
    drug_tolerance = Column(Integer, nullable=False)
    alcohol_comfort = Column(Integer, nullable=False)

    # Communication
    communication_directness = Column(Integer, nullable=False)
    communication_channel = Column(String, nullable=False)  # text, call, in_person, any
    response_time_expectation = Column(Integer, nullable=False)  # hours
    conflict_style = Column(String, nullable=False)  # collaborative, avoidant, assertive, compromising

    # Budget
    budget_stress = Column(Integer, nullable=False)
    expense_splitting_preference = Column(String, nullable=False)  # equal, by_usage, flexible

    # Values
    spirituality_importance = Column(Integer, nullable=False)
    political_discussion_comfort = Column(Integer, nullable=False)
    sustainability_importance = Column(Integer, nullable=False)

    # Open text
    dealbreakers = Column(ARRAY(String), nullable=False)
    flexible_on = Column(ARRAY(String), nullable=False)
    pet_peeves = Column(Text, nullable=True)
    ideal_roommate_description = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    resident = relationship("ResidentProfile", back_populates="questionnaire")


class OperatorOrg(Base):
    __tablename__ = "operator_orgs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    contact_email = Column(String, nullable=False)
    subscription_tier = Column(String, default="pilot")  # pilot, basic, pro, enterprise
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    members = relationship("OperatorMember", back_populates="org")
    properties = relationship("Property", back_populates="operator_org")
    match_runs = relationship("MatchRun", back_populates="operator_org")


class OperatorMember(Base):
    __tablename__ = "operator_members"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey("operator_orgs.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    role = Column(String, default="member")  # owner, admin, member
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    org = relationship("OperatorOrg", back_populates="members")
    user = relationship("User", back_populates="operator_memberships")


class Property(Base):
    __tablename__ = "properties"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    operator_org_id = Column(UUID(as_uuid=True), ForeignKey("operator_orgs.id"), nullable=False)
    name = Column(String, nullable=False)
    address = Column(String, nullable=False)
    city = Column(String, nullable=False)
    state = Column(String(2), nullable=False)
    zip_code = Column(String, nullable=False)
    total_units = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    operator_org = relationship("OperatorOrg", back_populates="properties")
    units = relationship("Unit", back_populates="property", cascade="all, delete-orphan")
    applicant_pools = relationship("ApplicantPool", back_populates="property")


class Unit(Base):
    __tablename__ = "units"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    property_id = Column(UUID(as_uuid=True), ForeignKey("properties.id"), nullable=False)
    unit_number = Column(String, nullable=False)
    total_rooms = Column(Integer, default=0)
    total_beds = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    property = relationship("Property", back_populates="units")
    rooms = relationship("Room", back_populates="unit", cascade="all, delete-orphan")


class Room(Base):
    __tablename__ = "rooms"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    unit_id = Column(UUID(as_uuid=True), ForeignKey("units.id"), nullable=False)
    room_number = Column(String, nullable=False)
    total_beds = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    unit = relationship("Unit", back_populates="rooms")
    beds = relationship("Bed", back_populates="room", cascade="all, delete-orphan")


class Bed(Base):
    __tablename__ = "beds"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    room_id = Column(UUID(as_uuid=True), ForeignKey("rooms.id"), nullable=False)
    bed_number = Column(String, nullable=False)
    is_occupied = Column(Boolean, default=False)
    current_resident_id = Column(UUID(as_uuid=True), ForeignKey("resident_profiles.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    room = relationship("Room", back_populates="beds")


class ApplicantPool(Base):
    __tablename__ = "applicant_pool"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resident_id = Column(UUID(as_uuid=True), ForeignKey("resident_profiles.id"), nullable=False)
    property_id = Column(UUID(as_uuid=True), ForeignKey("properties.id"), nullable=False)
    status = Column(String, default="pending")  # pending, approved, matched, rejected
    applied_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    resident = relationship("ResidentProfile", back_populates="applicant_pools")
    property = relationship("Property", back_populates="applicant_pools")


class MatchRun(Base):
    __tablename__ = "match_runs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    operator_org_id = Column(UUID(as_uuid=True), ForeignKey("operator_orgs.id"), nullable=False)
    property_id = Column(UUID(as_uuid=True), ForeignKey("properties.id"), nullable=False)
    bed_id = Column(UUID(as_uuid=True), ForeignKey("beds.id"), nullable=True)
    candidate_ids = Column(ARRAY(UUID(as_uuid=True)), nullable=False)
    group_size = Column(Integer, nullable=False, default=2)
    status = Column(SQLEnum(MatchRunStatus), nullable=False, default=MatchRunStatus.PENDING)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    operator_org = relationship("OperatorOrg", back_populates="match_runs")
    creator = relationship("User", back_populates="created_match_runs", foreign_keys=[created_by])
    match_results = relationship("MatchResult", back_populates="match_run", cascade="all, delete-orphan")


class MatchResult(Base):
    __tablename__ = "match_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    match_run_id = Column(UUID(as_uuid=True), ForeignKey("match_runs.id"), nullable=False)
    resident_a_id = Column(UUID(as_uuid=True), ForeignKey("resident_profiles.id"), nullable=False)
    resident_b_id = Column(UUID(as_uuid=True), ForeignKey("resident_profiles.id"), nullable=False)
    compatibility_score = Column(Float, nullable=False)  # 0-100
    risk_score = Column(Float, nullable=False)  # 0-1
    risk_level = Column(SQLEnum(RiskLevel), nullable=False)

    # JSON fields for detailed scores
    category_scores = Column(JSON, nullable=False)  # CategoryScores
    category_risks = Column(JSON, nullable=False)  # CategoryRisks
    top_alignments = Column(ARRAY(String), nullable=False)
    top_mismatches = Column(ARRAY(String), nullable=False)
    mitigation_tips = Column(ARRAY(String), nullable=False)
    recommended_house_rules = Column(ARRAY(String), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    match_run = relationship("MatchRun", back_populates="match_results")
    resident_a = relationship("ResidentProfile", back_populates="match_results_a", foreign_keys=[resident_a_id])
    resident_b = relationship("ResidentProfile", back_populates="match_results_b", foreign_keys=[resident_b_id])


class MoveIn(Base):
    __tablename__ = "move_ins"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resident_id = Column(UUID(as_uuid=True), ForeignKey("resident_profiles.id"), nullable=False)
    bed_id = Column(UUID(as_uuid=True), ForeignKey("beds.id"), nullable=False)
    move_in_date = Column(DateTime(timezone=True), nullable=False)
    move_out_date = Column(DateTime(timezone=True), nullable=True)
    is_renewed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    resident = relationship("ResidentProfile", back_populates="move_ins")


class ConflictReport(Base):
    __tablename__ = "conflict_reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    property_id = Column(UUID(as_uuid=True), ForeignKey("properties.id"), nullable=False)
    unit_id = Column(UUID(as_uuid=True), ForeignKey("units.id"), nullable=True)
    reported_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    category = Column(String, nullable=False)  # cleanliness, noise, guests, etc.
    severity = Column(SQLEnum(RiskLevel), nullable=False)
    description = Column(Text, nullable=False)
    resolution = Column(Text, nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class FeedbackSurvey(Base):
    __tablename__ = "feedback_surveys"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resident_id = Column(UUID(as_uuid=True), ForeignKey("resident_profiles.id"), nullable=False)
    survey_type = Column(String, nullable=False)  # 2_week, 8_week
    satisfaction_score = Column(Integer, nullable=False)  # 1-10
    match_accuracy_score = Column(Integer, nullable=False)  # 1-10
    would_recommend = Column(Boolean, nullable=False)
    feedback_text = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    resident = relationship("ResidentProfile", back_populates="feedback_surveys")


class Event(Base):
    __tablename__ = "events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_name = Column(String, nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    operator_org_id = Column(UUID(as_uuid=True), ForeignKey("operator_orgs.id"), nullable=True)
    properties = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    action = Column(String, nullable=False)
    entity_type = Column(String, nullable=False)
    entity_id = Column(UUID(as_uuid=True), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    changes = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)


class Lead(Base):
    __tablename__ = "leads"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_name = Column(String, nullable=False)
    contact_name = Column(String, nullable=False)
    contact_email = Column(String, nullable=False)
    contact_phone = Column(String, nullable=True)
    property_count = Column(Integer, nullable=True)
    unit_count = Column(Integer, nullable=True)
    message = Column(Text, nullable=True)
    status = Column(String, default="new")  # new, contacted, qualified, converted
    created_at = Column(DateTime(timezone=True), server_default=func.now())
