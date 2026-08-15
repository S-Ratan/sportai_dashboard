from fastapi import APIRouter, UploadFile, File, HTTPException
import os
import uuid

from app.db.supabase import supabase

from app.services.pose_service import analyze_video
from app.services.biomechanics_service import (
    process_frame,
    aggregate_biomechanics
)
from app.services.performance_engine import calculate_performance
from app.services.injury_engine import calculate_injury_risk


router = APIRouter(prefix="/api", tags=["Analysis"])

UPLOAD_DIR = "app/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {
    ".mp4",
    ".avi",
    ".mov",
    ".mkv"
}

# Your Supabase profile/user ID
DEMO_USER_ID = "5d3d7b87-9c51-43ca-8ca0-986de37b829c"


@router.post("/analyze")
async def analyze_video_endpoint(
    file: UploadFile = File(...)
):

    extension = os.path.splitext(file.filename)[1].lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Unsupported video format"
        )

    file_id = str(uuid.uuid4())

    filename = f"{file_id}{extension}"

    file_path = os.path.join(
        UPLOAD_DIR,
        filename
    )

    contents = await file.read()

    with open(file_path, "wb") as buffer:
        buffer.write(contents)

    try:

        # 1. Pose analysis
        analysis = analyze_video(file_path)

        # 2. Raw pose frames
        raw_frames = analysis.get("frame_data", [])

        # 3. Biomechanics
        biomechanics_frames = [
            process_frame(frame)
            for frame in raw_frames
        ]

        # 4. Aggregate biomechanics (ROM, velocity, asymmetry summary)
        biomechanics_summary = aggregate_biomechanics(biomechanics_frames)

        # 5. Performance
        performance = calculate_performance(
            biomechanics_frames
        )

        # 6. Injury risk
        injury = calculate_injury_risk(
            biomechanics_frames
        )

        # Add results to analysis
        analysis["biomechanics"] = biomechanics_frames
        analysis["biomechanics_summary"] = biomechanics_summary
        analysis["performance"] = performance
        analysis["injury_risk"] = injury

        # --------------------------------
        # SAVE VIDEO RECORD
        # --------------------------------

        video_data = {
            "id": file_id,
            "user_id": DEMO_USER_ID,
            "filename": file.filename,
            "storage_path": file_path,
            "sport": "Cricket",
            "status": "analyzed"
        }

        video_result = (
            supabase
            .table("videos")
            .insert(video_data)
            .execute()
        )

        # --------------------------------
        # SAVE ANALYSIS RECORD
        # --------------------------------

        analysis_data = {
            "user_id": DEMO_USER_ID,
            "video_id": file_id,
            "performance_score": performance.get(
                "performance_score", 0
            ),
            "performance_level": performance.get(
                "performance_level", "Unknown"
            ),
            "injury_risk_score": injury.get(
                "risk_score", 0
            ),
            "injury_risk_level": injury.get(
                "risk_level", "Unknown"
            ),
            "analysis_data": analysis
        }

        analysis_result = (
            supabase
            .table("analyses")
            .insert(analysis_data)
            .execute()
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Video analysis failed: {str(e)}"
        )

    return {
        "message": "Video analyzed and saved successfully",
        "file_id": file_id,
        "original_filename": file.filename,
        "analysis": analysis
    }