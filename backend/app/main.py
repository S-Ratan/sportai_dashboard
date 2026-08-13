from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(
    title="SportAI API",
    description="AI-Based Sports Performance Analysis and Injury Prevention System",
    version="1.0.0"
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