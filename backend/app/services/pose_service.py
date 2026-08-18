import cv2
import math
from pathlib import Path

import mediapipe as mp


# =========================================================
# MediaPipe Pose
# =========================================================

mp_pose = mp.solutions.pose


# =========================================================
# Configuration
# =========================================================

# Process one frame out of every three at a fixed,
# inference-friendly size.
FRAME_SIZE = (640, 360)
FRAME_SKIP = 3

MIN_LANDMARK_VISIBILITY = 0.0


# =========================================================
# Angle calculation
# =========================================================

def calculate_angle(a, b, c):
    """
    Calculate angle ABC from 2D points.

    Args:
        a: (x, y)
        b: (x, y)
        c: (x, y)

    Returns:
        Angle in degrees, between 0 and 180.
    """

    angle = math.degrees(
        math.atan2(c[1] - b[1], c[0] - b[0])
        - math.atan2(a[1] - b[1], a[0] - b[0])
    )

    angle = abs(angle)

    if angle > 180:
        angle = 360 - angle

    return round(angle, 2)


# =========================================================
# Convert MediaPipe landmark to point
# =========================================================

def point(landmark):
    """
    Convert a MediaPipe landmark into a 2D point.
    """

    return (
        landmark.x,
        landmark.y,
    )


# =========================================================
# Landmark serialization
# =========================================================

def landmark_data(landmark):
    """
    Convert a MediaPipe landmark into a JSON-safe dictionary.
    """

    return {
        "x": round(landmark.x, 5),
        "y": round(landmark.y, 5),
        "z": round(landmark.z, 5),
        "visibility": round(
            landmark.visibility,
            4,
        ),
    }


# =========================================================
# Analyze video
# =========================================================

def analyze_video(video_path: str):
    """
    Analyze a video using MediaPipe Pose.

    Returns:
        Dictionary containing:
        - status
        - frames
        - detected_frames
        - pose_detection_rate
        - average_knee_angle
        - average_hip_angle
        - average_elbow_angle
        - frame_data
    """

    path = Path(video_path)

    # -----------------------------------------------------
    # Validate video path
    # -----------------------------------------------------

    if not path.exists():
        raise FileNotFoundError(
            f"Video not found: {video_path}"
        )

    if not path.is_file():
        raise ValueError(
            f"Video path is not a file: {video_path}"
        )

    # -----------------------------------------------------
    # Open video
    # -----------------------------------------------------

    cap = cv2.VideoCapture(str(path))

    if not cap.isOpened():
        raise ValueError(
            f"Could not open video: {video_path}"
        )

    fps = cap.get(cv2.CAP_PROP_FPS)

    if not fps or fps <= 0:
        fps = 30.0

    frame_count = 0
    processed_frames = 0
    detected_frames = 0

    frame_data = []

    try:

        # -------------------------------------------------
        # MediaPipe Pose configuration
        # -------------------------------------------------

        with mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            smooth_landmarks=True,
            enable_segmentation=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        ) as pose:

            # ---------------------------------------------
            # Frame-by-frame processing
            # ---------------------------------------------

            while True:

                success, frame = cap.read()

                if not success:
                    break

                frame_count += 1

                # -----------------------------------------
                # Process every FRAME_SKIP-th frame
                # -----------------------------------------

                if (frame_count - 1) % FRAME_SKIP != 0:
                    continue

                processed_frames += 1

                # -----------------------------------------
                # Resize frame
                # -----------------------------------------

                frame = cv2.resize(
                    frame,
                    FRAME_SIZE,
                    interpolation=cv2.INTER_AREA,
                )

                # -----------------------------------------
                # BGR -> RGB
                # -----------------------------------------

                rgb_frame = cv2.cvtColor(
                    frame,
                    cv2.COLOR_BGR2RGB,
                )

                # -----------------------------------------
                # Timestamp
                # -----------------------------------------

                timestamp_ms = int(
                    (frame_count - 1) * 1000 / fps
                )

                # -----------------------------------------
                # Pose detection
                # -----------------------------------------

                result = pose.process(rgb_frame)

                # -----------------------------------------
                # No pose detected
                # -----------------------------------------

                if not result.pose_landmarks:
                    continue

                detected_frames += 1

                # -----------------------------------------
                # Get landmarks
                # -----------------------------------------

                landmarks = result.pose_landmarks.landmark

                # =================================================
                # RIGHT SIDE
                # =================================================

                rs = landmarks[
                    mp_pose.PoseLandmark.RIGHT_SHOULDER
                ]

                re = landmarks[
                    mp_pose.PoseLandmark.RIGHT_ELBOW
                ]

                rw = landmarks[
                    mp_pose.PoseLandmark.RIGHT_WRIST
                ]

                rh = landmarks[
                    mp_pose.PoseLandmark.RIGHT_HIP
                ]

                rk = landmarks[
                    mp_pose.PoseLandmark.RIGHT_KNEE
                ]

                ra = landmarks[
                    mp_pose.PoseLandmark.RIGHT_ANKLE
                ]

                rf = landmarks[
                    mp_pose.PoseLandmark.RIGHT_FOOT_INDEX
                ]

                # =================================================
                # LEFT SIDE
                # =================================================

                ls = landmarks[
                    mp_pose.PoseLandmark.LEFT_SHOULDER
                ]

                le = landmarks[
                    mp_pose.PoseLandmark.LEFT_ELBOW
                ]

                lw = landmarks[
                    mp_pose.PoseLandmark.LEFT_WRIST
                ]

                lh = landmarks[
                    mp_pose.PoseLandmark.LEFT_HIP
                ]

                lk = landmarks[
                    mp_pose.PoseLandmark.LEFT_KNEE
                ]

                la = landmarks[
                    mp_pose.PoseLandmark.LEFT_ANKLE
                ]

                lf = landmarks[
                    mp_pose.PoseLandmark.LEFT_FOOT_INDEX
                ]

                # =================================================
                # Convert landmarks to 2D points
                # =================================================

                right_shoulder = point(rs)
                right_elbow = point(re)
                right_wrist = point(rw)

                right_hip = point(rh)
                right_knee = point(rk)
                right_ankle = point(ra)
                right_foot = point(rf)

                left_shoulder = point(ls)
                left_elbow = point(le)
                left_wrist = point(lw)

                left_hip = point(lh)
                left_knee = point(lk)
                left_ankle = point(la)
                left_foot = point(lf)

                # =================================================
                # Joint angles
                # =================================================

                right_elbow_angle = calculate_angle(
                    right_shoulder,
                    right_elbow,
                    right_wrist,
                )

                left_elbow_angle = calculate_angle(
                    left_shoulder,
                    left_elbow,
                    left_wrist,
                )

                right_knee_angle = calculate_angle(
                    right_hip,
                    right_knee,
                    right_ankle,
                )

                left_knee_angle = calculate_angle(
                    left_hip,
                    left_knee,
                    left_ankle,
                )

                right_hip_angle = calculate_angle(
                    right_shoulder,
                    right_hip,
                    right_knee,
                )

                left_hip_angle = calculate_angle(
                    left_shoulder,
                    left_hip,
                    left_knee,
                )

                right_ankle_angle = calculate_angle(
                    right_knee,
                    right_ankle,
                    right_foot,
                )

                left_ankle_angle = calculate_angle(
                    left_knee,
                    left_ankle,
                    left_foot,
                )

                right_shoulder_angle = calculate_angle(
                    right_elbow,
                    right_shoulder,
                    right_hip,
                )

                left_shoulder_angle = calculate_angle(
                    left_elbow,
                    left_shoulder,
                    left_hip,
                )

                # =================================================
                # Store frame data
                # =================================================

                frame_data.append(
                    {
                        "frame": frame_count,

                        "timestamp_ms": timestamp_ms,

                        "timestamp_seconds": round(
                            timestamp_ms / 1000,
                            3,
                        ),

                        # -----------------------------------------
                        # Right landmarks
                        # -----------------------------------------

                        "right_shoulder": landmark_data(rs),

                        "right_elbow": landmark_data(re),

                        "right_wrist": landmark_data(rw),

                        "right_hip": landmark_data(rh),

                        "right_knee": landmark_data(rk),

                        "right_ankle": landmark_data(ra),

                        "right_foot": landmark_data(rf),

                        # -----------------------------------------
                        # Left landmarks
                        # -----------------------------------------

                        "left_shoulder": landmark_data(ls),

                        "left_elbow": landmark_data(le),

                        "left_wrist": landmark_data(lw),

                        "left_hip": landmark_data(lh),

                        "left_knee": landmark_data(lk),

                        "left_ankle": landmark_data(la),

                        "left_foot": landmark_data(lf),

                        # -----------------------------------------
                        # Angles
                        # -----------------------------------------

                        "right_elbow_angle": right_elbow_angle,

                        "left_elbow_angle": left_elbow_angle,

                        "right_knee_angle": right_knee_angle,

                        "left_knee_angle": left_knee_angle,

                        "right_hip_angle": right_hip_angle,

                        "left_hip_angle": left_hip_angle,

                        "right_ankle_angle": right_ankle_angle,

                        "left_ankle_angle": left_ankle_angle,

                        "right_shoulder_angle": right_shoulder_angle,

                        "left_shoulder_angle": left_shoulder_angle,
                    }
                )

    finally:

        # -----------------------------------------------------
        # Always release video
        # -----------------------------------------------------

        cap.release()

    # =========================================================
    # No pose detected
    # =========================================================

    if detected_frames == 0:

        return {
            "status": "no_pose_detected",
            "frames": frame_count,
            "processed_frames": processed_frames,
            "detected_frames": 0,
            "pose_detection_rate": 0,
            "average_knee_angle": None,
            "average_hip_angle": None,
            "average_elbow_angle": None,
            "frame_data": [],
        }

    # =========================================================
    # Calculate averages
    # =========================================================

    right_knee_angles = [
        item["right_knee_angle"]
        for item in frame_data
    ]

    right_hip_angles = [
        item["right_hip_angle"]
        for item in frame_data
    ]

    right_elbow_angles = [
        item["right_elbow_angle"]
        for item in frame_data
    ]

    # ---------------------------------------------------------
    # Avoid division by zero
    # ---------------------------------------------------------

    average_knee_angle = (
        round(
            sum(right_knee_angles)
            / len(right_knee_angles),
            2,
        )
        if right_knee_angles
        else None
    )

    average_hip_angle = (
        round(
            sum(right_hip_angles)
            / len(right_hip_angles),
            2,
        )
        if right_hip_angles
        else None
    )

    average_elbow_angle = (
        round(
            sum(right_elbow_angles)
            / len(right_elbow_angles),
            2,
        )
        if right_elbow_angles
        else None
    )

    # =========================================================
    # Final result
    # =========================================================

    return {
        "status": "analysis_complete",

        "frames": frame_count,

        "processed_frames": processed_frames,

        "detected_frames": detected_frames,

        "pose_detection_rate": round(
            detected_frames / processed_frames * 100,
            2,
        )
        if processed_frames > 0
        else 0,

        "average_knee_angle": average_knee_angle,

        "average_hip_angle": average_hip_angle,

        "average_elbow_angle": average_elbow_angle,

        "frame_data": frame_data,
    }