"""Technical quality indicators for a pose analysis (not clinical confidence)."""
from typing import Any, Dict, List


LANDMARK_KEYS = (
    "left_shoulder", "right_shoulder", "left_elbow", "right_elbow",
    "left_wrist", "right_wrist", "left_hip", "right_hip",
    "left_knee", "right_knee", "left_ankle", "right_ankle",
)


def calculate_analysis_quality(analysis: Dict[str, Any]) -> Dict[str, Any]:
    """Return an explainable 0-100 technical quality indicator.

    This assesses data availability only; it does not represent diagnostic or
    scientific accuracy.
    """
    total_frames = max(int(analysis.get("frames") or 0), 0)
    detected_frames = max(int(analysis.get("detected_frames") or 0), 0)
    frames: List[Dict[str, Any]] = analysis.get("frame_data") or []
    detection_rate = round((detected_frames / total_frames * 100), 2) if total_frames else 0.0

    visible = 0
    possible = len(frames) * len(LANDMARK_KEYS)
    for frame in frames:
        visible += sum(
            1 for key in LANDMARK_KEYS
            if isinstance(frame.get(key), dict) and frame[key].get("visibility", 0) >= 0.25
        )
    completeness = round((visible / possible * 100), 2) if possible else 0.0
    usable_rate = round((len(frames) / total_frames * 100), 2) if total_frames else 0.0

    # Availability is deliberately rounded to a whole number to avoid false precision.
    score = round(0.55 * detection_rate + 0.25 * completeness + 0.20 * usable_rate)
    warnings: List[str] = []
    if detection_rate < 60:
        warnings.append(f"Pose was detected in only {detection_rate:.2f}% of frames.")
    if completeness < 75 and frames:
        warnings.append("Some detected frames have incomplete visible landmarks.")
    if total_frames < 15:
        warnings.append("The video contains few frames; movement coverage is limited.")
    if not frames:
        warnings.append("No usable pose frames were available for analysis.")

    level = "High" if score >= 80 else "Moderate" if score >= 55 else "Low"
    return {
        "analysis_confidence": score,
        "analysis_quality": score,
        "quality_level": level,
        "quality_warnings": warnings,
        "technical_factors": {
            "pose_detection_rate": detection_rate,
            "usable_frame_rate": usable_rate,
            "landmark_completeness": completeness,
        },
    }
