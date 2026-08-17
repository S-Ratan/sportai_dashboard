import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.services.quality_service import calculate_analysis_quality
from app.services.recommendation_engine import generate_recommendations
from app.api.routes import _validate_upload
from fastapi import HTTPException


def _frame(visibility=0.9):
    return {key: {"visibility": visibility} for key in (
        "left_shoulder", "right_shoulder", "left_elbow", "right_elbow",
        "left_wrist", "right_wrist", "left_hip", "right_hip",
        "left_knee", "right_knee", "left_ankle", "right_ankle",
    )}


def test_quality_uses_measurable_frame_availability():
    result = calculate_analysis_quality({"frames": 10, "detected_frames": 5, "frame_data": [_frame() for _ in range(5)]})
    assert result["technical_factors"]["pose_detection_rate"] == 50.0
    assert result["quality_level"] == "Moderate"
    assert "50.00%" in result["quality_warnings"][0]


def test_quality_handles_missing_pose_data():
    result = calculate_analysis_quality({"frames": 12, "detected_frames": 0, "frame_data": []})
    assert result["analysis_confidence"] == 0
    assert result["quality_level"] == "Low"


def test_recommendations_only_include_triggered_metrics():
    risk = {"metrics": {"average_knee_asymmetry": 12, "average_trunk_tilt": 4}}
    recommendations = generate_recommendations({}, {}, risk, {"quality_level": "High", "analysis_confidence": 90})
    assert len(recommendations) == 1
    assert recommendations[0]["metric"] == "knee_asymmetry"


def test_low_quality_adds_capture_guidance():
    recommendations = generate_recommendations({}, {}, {"metrics": {}}, {"quality_level": "Low", "analysis_confidence": 20})
    assert recommendations[0]["category"] == "Analysis quality"


def test_upload_validation_rejects_invalid_and_empty_files():
    for filename, data, expected_status in (("clip.exe", b"x", 415), ("clip.mp4", b"", 422)):
        try:
            _validate_upload(filename, data)
            assert False, "validation should fail"
        except HTTPException as error:
            assert error.status_code == expected_status


if __name__ == "__main__":
    for test in (
        test_quality_uses_measurable_frame_availability, test_quality_handles_missing_pose_data,
        test_recommendations_only_include_triggered_metrics, test_low_quality_adds_capture_guidance,
        test_upload_validation_rejects_invalid_and_empty_files,
    ):
        test()
    print("Quality and recommendation tests passed")
