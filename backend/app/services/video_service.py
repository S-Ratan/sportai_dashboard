import cv2
from pathlib import Path


def get_video_info(video_path: str) -> dict:
    """
    Extract basic information from a video.
    """

    path = Path(video_path)

    if not path.exists():
        raise FileNotFoundError(f"Video not found: {video_path}")

    cap = cv2.VideoCapture(str(path))

    if not cap.isOpened():
        raise ValueError("Could not open video")

    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    duration = frame_count / fps if fps > 0 else 0

    cap.release()

    return {
        "filename": path.name,
        "fps": fps,
        "frame_count": frame_count,
        "width": width,
        "height": height,
        "duration_seconds": duration,
    }


def extract_frames(video_path: str, max_frames: int = 100) -> list:
    """
    Extract frames from a video.
    """

    path = Path(video_path)

    if not path.exists():
        raise FileNotFoundError(f"Video not found: {video_path}")

    cap = cv2.VideoCapture(str(path))

    if not cap.isOpened():
        raise ValueError("Could not open video")

    frames = []

    while len(frames) < max_frames:
        success, frame = cap.read()

        if not success:
            break

        frames.append(frame)

    cap.release()

    return frames