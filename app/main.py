from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.models import (
    FinancialProfile,
    TransitionPlan,
    ResumeAnalysisRequest,
    ResumeAnalysisResponse,
)
from app.logic import FinancialBridge
from app.services.resume_analysis import analyze_resume

app = FastAPI(
    title="Career Transition Calculator API",
    description="Financial analysis API for career transitions",
    version="1.0.0",
)

# Configure CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Career Transition Calculator API",
        "version": "1.0.0",
        "endpoints": {
            "/analyze": "POST - Analyze financial profile for career transition",
            "/resume/analyze": "POST - Analyze resume for career guidance",
            "/health": "GET - Health check endpoint",
        },
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "career-transition-api"}


@app.post("/analyze", response_model=TransitionPlan)
async def analyze_transition(profile: FinancialProfile) -> TransitionPlan:
    """
    Analyze financial profile and generate transition plan.
    """
    try:
        plan = FinancialBridge.calculate(profile)
        return plan
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Validation error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.post("/resume/analyze", response_model=ResumeAnalysisResponse)
async def analyze_resume_endpoint(payload: ResumeAnalysisRequest) -> ResumeAnalysisResponse:
    """Analyze a resume (text) and return structured career recommendations."""
    try:
        context = {
            "target_role": payload.target_role,
            "current_location": payload.current_location,
            "preferred_location": payload.preferred_location,
            "work_mode": payload.work_mode,
            "years_experience": payload.years_experience,
        }
        result = analyze_resume(payload.resume_text, payload.intent, context)
        return ResumeAnalysisResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Validation error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Resume analysis failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
