from typing import Dict, List, Optional, Literal
from pydantic import BaseModel, Field

# --- NEW: Resume Analysis Models ---
class ResumeAnalysisRequest(BaseModel):
    resume_text: str = Field(..., description="Raw extracted resume text")
    intent: Literal["A", "B", "C", "D"] = Field(..., description="User intent: A/B/C/D")
    target_role: Optional[str] = Field(None, description="Target role if provided")
    current_location: Optional[str] = None
    preferred_location: Optional[str] = None
    work_mode: Optional[str] = Field(None, description="remote/hybrid/onsite")
    years_experience: Optional[float] = None


class ResumeRecommendation(BaseModel):
    role: str
    match: int
    why: str
    matched: List[str]
    gaps: List[str]
    nice_to_have: List[str]


class ResumeAnalysisResponse(BaseModel):
    summary: str
    strengths: List[str]
    titles: List[str]
    skills: List[str]
    soft_skills: List[str]
    domains: List[str]
    level: str
    track: str
    recommendations: List[ResumeRecommendation]
    gaps: List[str]
    action_plan: List[str]
    next_steps: List[str]
    intent: str
    user_context: Dict


# --- EXISTING: AI Advice Structure ---
class LearningResource(BaseModel):
    name: str
    cost: str
    url: Optional[str] = None


class AIStrategy(BaseModel):
    verdict: str = Field(..., description="Risk assessment: Low, Medium, High")
    action_plan: List[str] = Field(..., description="Immediate steps to take")
    resources: List[LearningResource] = Field(..., description="Recommended courses/books")


# --- EXISTING: Financial Models (Kept valid) ---
class FinancialProfile(BaseModel):
    current_salary: float = Field(..., gt=0)
    monthly_expenses: float = Field(..., gt=0)
    current_savings: float = Field(..., ge=0)
    transition_months: int = Field(..., gt=0)
    new_salary: Optional[float] = Field(None)
    emergency_fund_months: int = Field(3)


class TransitionPlan(BaseModel):
    # Financials
    monthly_burn_rate: float
    total_runway_months: float
    capital_gap: float
    is_financially_ready: bool

    # The New "Brain" Section
    strategy: AIStrategy
