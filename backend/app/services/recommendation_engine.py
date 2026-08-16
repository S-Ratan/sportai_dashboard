"""Metric-based movement recommendations for screening, not diagnosis."""
from typing import Any, Dict, List, Optional


def _recommendation(category: str, severity: str, metric: str, value: float,
                    threshold: float, explanation: str, recommendation: str) -> Dict[str, Any]:
    return {"category": category, "severity": severity, "metric": metric,
            "observed_value": round(value, 2), "threshold": threshold,
            "explanation": explanation, "recommendation": recommendation}


def generate_recommendations(biomechanics: Optional[Dict[str, Any]], performance: Dict[str, Any],
                             injury_risk: Dict[str, Any], confidence: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate only recommendations supported by calculated metrics."""
    del biomechanics, performance  # Reserved for future model-specific rules.
    metrics = injury_risk.get("metrics") or {}
    rules = (
        ("Lower body", "knee_asymmetry", "average_knee_asymmetry", 8,
         "Significant left/right knee movement asymmetry was detected.",
         "Review lower-body symmetry and landing mechanics with a qualified coach."),
        ("Lower body", "hip_asymmetry", "average_hip_asymmetry", 8,
         "Noticeable left/right hip movement asymmetry was detected.",
         "Review hip control and movement symmetry with a qualified coach."),
        ("Upper body", "elbow_asymmetry", "average_elbow_asymmetry", 15,
         "Noticeable elbow movement asymmetry was detected.",
         "Review upper-body technique and movement consistency."),
        ("Trunk control", "trunk_tilt", "average_trunk_tilt", 8,
         "Excessive trunk inclination was detected.",
         "Review trunk control and technique during the movement."),
        ("Shoulder control", "shoulder_symmetry", "average_shoulder_symmetry", 0.04,
         "Shoulder height asymmetry was detected in the pose data.",
         "Review upper-body control with a qualified coach or health professional if it persists."),
    )
    results: List[Dict[str, Any]] = []
    for category, metric, source, threshold, explanation, advice in rules:
        value = metrics.get(source)
        if isinstance(value, (int, float)) and value > threshold:
            severity = "High" if value > threshold * 1.75 else "Moderate"
            results.append(_recommendation(category, severity, metric, value, threshold, explanation, advice))
    if confidence.get("quality_level") == "Low":
        results.append(_recommendation("Analysis quality", "Low", "analysis_confidence",
            confidence.get("analysis_confidence", 0), 55,
            "Limited pose coverage reduces the reliability of this movement screening.",
            "Capture a clearer, full-body video from a stable camera angle and repeat the analysis."))
    return results
