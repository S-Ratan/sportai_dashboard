"""Video analysis endpoints. Persistence is performed by the authenticated frontend.

The browser Supabase client carries the user's session, allowing RLS to enforce
athlete isolation. The API deliberately does not accept a caller-supplied user id.
"""
import logging
import os
import uuid
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.schemas import AnalysisResponse
from app.services.biomechanics_service import aggregate_biomechanics, build_biomechanics_chart, process_frame
from app.services.models import RuleBasedPerformanceModel, RuleBasedRiskModel
from app.services.pose_service import analyze_video
from app.services.quality_service import calculate_analysis_quality
from app.services.recommendation_engine import generate_recommendations
from app.services.video_service import get_video_info

router = APIRouter(prefix="/api", tags=["Analysis"])
logger = logging.getLogger(__name__)
UPLOAD_DIR = Path(__file__).resolve().parents[1] / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)
ALLOWED_EXTENSIONS = {".mp4", ".avi", ".mov", ".mkv"}
MAX_UPLOAD_BYTES = int(os.getenv("SPORTAI_MAX_UPLOAD_BYTES", str(100 * 1024 * 1024)))


def _validate_upload(filename: str, contents: bytes) -> str:
    extension = Path(filename or "").suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(415, "Unsupported video format. Use MP4, AVI, MOV, or MKV.")
    if not contents:
        raise HTTPException(422, "The uploaded video is empty.")
    if len(contents) > MAX_UPLOAD_BYTES:
        raise HTTPException(413, f"Video exceeds the {MAX_UPLOAD_BYTES // (1024 * 1024)} MB upload limit.")
    return extension


def _public_analysis_error(error: OSError | ValueError, upload_path: Path) -> str:
    """Keep the cause useful without returning the container's filesystem paths."""
    return str(error).replace(str(upload_path), "uploaded video")


def run_analysis(video_path: str) -> dict:
    """Run the existing pipeline and enrich its backward-compatible result."""
    info = get_video_info(video_path)
    if info["frame_count"] < 2 or info["duration_seconds"] <= 0:
        raise ValueError("Video is too short to analyze.")
    analysis = analyze_video(video_path)
    frames = [process_frame(frame) for frame in analysis.get("frame_data", [])]
    biomechanics = aggregate_biomechanics(frames)
    performance = RuleBasedPerformanceModel().predict(frames)
    injury_risk = RuleBasedRiskModel().predict(frames)
    quality = calculate_analysis_quality(analysis)
    analysis.update({
        "video_info": info,
        "biomechanics": frames,
        "biomechanics_summary": biomechanics,
        "biomechanics_chart": build_biomechanics_chart(biomechanics),
        "performance": performance,
        "injury_risk": injury_risk,
        **quality,
    })
    analysis["recommendations"] = generate_recommendations(
        biomechanics, performance, injury_risk, quality
    )
    return analysis


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_video_endpoint(file: UploadFile = File(...)):
    """Analyze a supported video and return one report payload for authenticated persistence."""
    contents = await file.read()
    extension = _validate_upload(file.filename or "", contents)
    analysis_id = str(uuid.uuid4())
    file_id = str(uuid.uuid4())
    path = UPLOAD_DIR / f"{file_id}{extension}"
    try:
        path.write_bytes(contents)
        analysis = run_analysis(str(path))
    except HTTPException:
        raise
    except (ValueError, OSError) as error:
        logger.exception("Video analysis could not process upload %s", path.name)
        raise HTTPException(
            422,
            f"Video could not be analyzed: {_public_analysis_error(error, path)}",
        ) from error
    except Exception as error:
        logger.exception("Unexpected video analysis failure for upload %s", path.name)
        # Do not expose implementation details or local paths to clients.
        raise HTTPException(500, "Video analysis failed. Please try a valid, clear video.") from error
    finally:
        path.unlink(missing_ok=True)
    return {
        "message": "Video analyzed successfully",
        "analysis_id": analysis_id,
        "file_id": file_id,
        "original_filename": Path(file.filename or "video").name,
        "analysis": analysis,
    }
