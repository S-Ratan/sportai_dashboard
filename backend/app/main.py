from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router

app = FastAPI(
    title="SportAI API",
    description="AI-Based Sports Performance Analysis and Injury Prevention System",
    version="1.0.0"
)

# --- ADD CORS MIDDLEWARE HERE ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/")
def root():
    return {
        "message": "SportAI API is running"
    }


@app.get("/api/health")
def health():
    return {
        "status": "healthy",
        "service": "SportAI Backend"
    }