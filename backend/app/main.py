from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router


app = FastAPI(
    title="SportAI API",
    description="AI-Based Sports Performance Analysis and Injury Prevention System",
    version="1.0.0",
)


# ============================================================
# CORS CONFIGURATION
# ============================================================

ALLOWED_ORIGINS = [
    # Local development
    "http://localhost:5173",
    "http://127.0.0.1:5173",

    # Vercel production frontend (stable alias)
    "https://sportai-dashboard-jade.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,

    # Allow every Vercel preview/branch/hash deployment for this project
    # (e.g. sportai-dashboard-git-main-ratan-code.vercel.app,
    #  sportai-dashboard-cjciee7ns-ratan-code.vercel.app)
    # plus Netlify deployments/subdomains.
    allow_origin_regex=r"https://sportai-dashboard(-[a-z0-9-]+)?\.vercel\.app|https://[a-z0-9-]+\.netlify\.app",

    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# API ROUTES
# ============================================================

app.include_router(router)


# ============================================================
# ROOT ENDPOINT
# ============================================================

@app.get("/")
def root():
    return {
        "message": "SportAI API is running"
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/api/health")
def health():
    return {
        "status": "healthy",
        "service": "SportAI Backend"
    }