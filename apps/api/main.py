from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from routers import auth, resident, operator, admin, public

app = FastAPI(
    title="Lease Peace API",
    description="Roommate matching and conflict prediction platform",
    version="0.1.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(resident.router)
app.include_router(operator.router)
app.include_router(admin.router)
app.include_router(public.router)


@app.get("/")
def root():
    return {
        "message": "Lease Peace API",
        "version": "0.1.0",
        "docs": "/docs"
    }
