from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class Recommendation(BaseModel):
    category: str
    severity: str
    metric: str
    observed_value: float
    threshold: float
    explanation: str
    recommendation: str


class AnalysisResponse(BaseModel):
    message: str
    analysis_id: str
    file_id: str
    original_filename: str
    analysis: Dict[str, Any]


class ProgressSession(BaseModel):
    date: str
    performance_score: Optional[float] = None
    injury_risk_score: Optional[float] = None
    pose_detection_rate: Optional[float] = None
    metrics: Dict[str, Optional[float]] = Field(default_factory=dict)
