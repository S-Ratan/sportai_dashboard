import cv2
import math
from pathlib import Path

import mediapipe as mp


# ---------------------------------------------------------
# MediaPipe Tasks API
# ---------------------------------------------------------

BaseOptions = mp.tasks.BaseOptions
VisionRunningMode = mp.tasks.vision.RunningMode
PoseLandmarker = mp.tasks.vision.PoseLandmarker
PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
PoseLandmark = mp.tasks.vision.PoseLandmark


# ---------------------------------------------------------
# Model path
# ---------------------------------------------------------

MODEL_PATH = (
    Path(__file__).resolve().parents[2]
    / "models"
    / "pose_landmarker_full.task"
)


# ---------------------------------------------------------
# Angle calculation
# ---------------------------------------------------------

def calculate_angle(a, b, c):
    """
    Calculate angle ABC using three 2D points.
    """

    angle = math.degrees(
        math.atan2(c[1] - b[1], c[0] - b[0])
        - math.atan2(a[1] - b[1], a[0] - b[0])
    )

    angle = abs(angle)

    if angle > 180:
        angle = 360 - angle

    return round(angle, 2)


# ---------------------------------------------------------
# Analyze video
# ---------------------------------------------------------

def analyze_video(video_path: str):

    video_path = str(video_path)

    # -----------------------------------------------------
    # Open video
    # -----------------------------------------------------

    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        raise ValueError(
            f"Could not open video: {video_path}"
        )

    # -----------------------------------------------------
    # Counters
    # -----------------------------------------------------

    frame_count = 0
    detected_frames = 0

    # IMPORTANT:
    # MediaPipe VIDEO mode requires strictly increasing
    # timestamps.
    last_timestamp_ms = -1

    # -----------------------------------------------------
    # Results
    # -----------------------------------------------------

    knee_angles = []
    hip_angles = []
    elbow_angles = []

    # -----------------------------------------------------
    # Check model
    # -----------------------------------------------------

    if not MODEL_PATH.exists():
        cap.release()

        raise FileNotFoundError(
            f"MediaPipe model not found: {MODEL_PATH}"
        )

    # -----------------------------------------------------
    # MediaPipe PoseLandmarker configuration
    # -----------------------------------------------------

    base_options = BaseOptions(
        model_asset_path=str(MODEL_PATH)
    )

    options = PoseLandmarkerOptions(
        base_options=base_options,
        running_mode=VisionRunningMode.VIDEO,
        num_poses=1,
        min_pose_detection_confidence=0.5,
        min_pose_presence_confidence=0.5,
        min_tracking_confidence=0.5,
        output_segmentation_masks=False,
    )

    # -----------------------------------------------------
    # Create PoseLandmarker
    # -----------------------------------------------------

    with PoseLandmarker.create_from_options(
        options
    ) as landmarker:

        while True:

            # -------------------------------------------------
            # Read frame
            # -------------------------------------------------

            success, frame = cap.read()

            if not success:
                break

            frame_count += 1

            # -------------------------------------------------
            # OpenCV BGR -> RGB
            # -------------------------------------------------

            rgb_frame = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2RGB
            )

            # -------------------------------------------------
            # Convert to MediaPipe Image
            # -------------------------------------------------

            mp_image = mp.Image(
                image_format=mp.ImageFormat.SRGB,
                data=rgb_frame
            )

            # -------------------------------------------------
            # Generate reliable timestamp
            # -------------------------------------------------

            fps = cap.get(cv2.CAP_PROP_FPS)

            if not fps or fps <= 0:
                fps = 30.0

            timestamp_ms = int(
                (frame_count - 1) * 1000 / fps
            )

            # -------------------------------------------------
            # IMPORTANT:
            # MediaPipe requires timestamps to be strictly
            # increasing.
            # -------------------------------------------------

            if timestamp_ms <= last_timestamp_ms:
                timestamp_ms = last_timestamp_ms + 1

            last_timestamp_ms = timestamp_ms

            # -------------------------------------------------
            # Run MediaPipe Pose Detection
            # -------------------------------------------------

            result = landmarker.detect_for_video(
                mp_image,
                timestamp_ms
            )

            # -------------------------------------------------
            # Check if pose detected
            # -------------------------------------------------

            if not result.pose_landmarks:
                continue

            if len(result.pose_landmarks) == 0:
                continue

            detected_frames += 1

            # -------------------------------------------------
            # First detected person
            # -------------------------------------------------

            landmarks = result.pose_landmarks[0]

            # -------------------------------------------------
            # Get right-side landmarks
            # -------------------------------------------------

            right_shoulder = landmarks[
                PoseLandmark.RIGHT_SHOULDER
            ]

            right_elbow = landmarks[
                PoseLandmark.RIGHT_ELBOW
            ]

            right_wrist = landmarks[
                PoseLandmark.RIGHT_WRIST
            ]

            right_hip = landmarks[
                PoseLandmark.RIGHT_HIP
            ]

            right_knee = landmarks[
                PoseLandmark.RIGHT_KNEE
            ]

            right_ankle = landmarks[
                PoseLandmark.RIGHT_ANKLE
            ]

            # -------------------------------------------------
            # Convert landmarks to 2D points
            # -------------------------------------------------

            shoulder = (
                right_shoulder.x,
                right_shoulder.y
            )

            elbow = (
                right_elbow.x,
                right_elbow.y
            )

            wrist = (
                right_wrist.x,
                right_wrist.y
            )

            hip = (
                right_hip.x,
                right_hip.y
            )

            knee = (
                right_knee.x,
                right_knee.y
            )

            ankle = (
                right_ankle.x,
                right_ankle.y
            )

            # -------------------------------------------------
            # Calculate joint angles
            # -------------------------------------------------

            elbow_angle = calculate_angle(
                shoulder,
                elbow,
                wrist
            )

            hip_angle = calculate_angle(
                shoulder,
                hip,
                knee
            )

            knee_angle = calculate_angle(
                hip,
                knee,
                ankle
            )

            # -------------------------------------------------
            # Store results
            # -------------------------------------------------

            elbow_angles.append(elbow_angle)
            hip_angles.append(hip_angle)
            knee_angles.append(knee_angle)

    # ---------------------------------------------------------
    # Release video
    # ---------------------------------------------------------

    cap.release()

    # ---------------------------------------------------------
    # No pose detected
    # ---------------------------------------------------------

    if detected_frames == 0:

        return {
            "status": "no_pose_detected",
            "frames": frame_count,
            "detected_frames": 0,
            "pose_detection_rate": 0,
        }

    # ---------------------------------------------------------
    # Final analysis
    # ---------------------------------------------------------

    return {
        "status": "analysis_complete",

        "frames": frame_count,

        "detected_frames": detected_frames,

        "pose_detection_rate": round(
            detected_frames / frame_count * 100,
            2
        ),

        "average_knee_angle": round(
            sum(knee_angles) / len(knee_angles),
            2
        ) if knee_angles else None,

        "average_hip_angle": round(
            sum(hip_angles) / len(hip_angles),
            2
        ) if hip_angles else None,

        "average_elbow_angle": round(
            sum(elbow_angles) / len(elbow_angles),
            2
        ) if elbow_angles else None,
    }