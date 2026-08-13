from fastapi import APIRouter, UploadFile, File, HTTPException
import os
import uuid

from app.services.pose_service import analyze_video


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

        analysis = analyze_video(file_path)

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