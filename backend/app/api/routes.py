from fastapi import APIRouter, UploadFile, File, HTTPException
import os
import uuid

from app.services.pose_service import analyze_video
from app.services.biomechanics_service import process_frame
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


@router.post("/analyze")
async def analyze_video_endpoint(
    file: UploadFile = File(...)
):

    extension = os.path.splitext(
        file.filename
    )[1].lower()

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

        # Step 1: Pose analysis
        analysis = analyze_video(file_path)

        # Step 2: Get raw pose frames
        raw_frames = analysis.get(
            "frame_data",
            []
        )

        # Step 3: Calculate biomechanics
        # for every detected frame
        biomechanics_frames = [
            process_frame(frame)
            for frame in raw_frames
        ]

        # Step 4: Calculate performance
        performance = calculate_performance(
            biomechanics_frames
        )

        # Step 5: Calculate injury risk
        injury = calculate_injury_risk(
            biomechanics_frames
        )

        # Step 6: Add results to analysis
        analysis["biomechanics"] = biomechanics_frames

        analysis["performance"] = performance

        analysis["injury_risk"] = injury

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Video analysis failed: {str(e)}"
        )

    return {
        "message": "Video analyzed successfully",
        "file_id": file_id,
        "original_filename": file.filename,
        "analysis": analysis
    }