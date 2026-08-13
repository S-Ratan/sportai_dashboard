import cv2
import math
from pathlib import Path

import mediapipe as mp


# =========================================================
# MediaPipe Tasks API
# =========================================================

BaseOptions = mp.tasks.BaseOptions
VisionRunningMode = mp.tasks.vision.RunningMode
PoseLandmarker = mp.tasks.vision.PoseLandmarker
PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
PoseLandmark = mp.tasks.vision.PoseLandmark


# =========================================================
# Model
# =========================================================

MODEL_PATH = (
    Path(__file__).resolve().parents[2]
    / "models"
    / "pose_landmarker_full.task"
)


# =========================================================
# Angle calculation
# =========================================================

def calculate_angle(a, b, c):
    """
    Calculate angle ABC from 2D points.
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
    return (
        landmark.x,
        landmark.y
    )


# =========================================================
# Analyze video
# =========================================================

def analyze_video(video_path: str):

    path = Path(video_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Video not found: {video_path}"
        )

    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"MediaPipe model not found: {MODEL_PATH}"
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
    detected_frames = 0

    last_timestamp_ms = -1

    # -----------------------------------------------------
    # Frame-by-frame data
    # -----------------------------------------------------

    frame_data = []

    # -----------------------------------------------------
    # MediaPipe configuration
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
    # Create landmarker
    # -----------------------------------------------------

    with PoseLandmarker.create_from_options(
        options
    ) as landmarker:

        while True:

            success, frame = cap.read()

            if not success:
                break

            frame_count += 1

            # -------------------------------------------------
            # BGR -> RGB
            # -------------------------------------------------

            rgb_frame = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2RGB
            )

            # -------------------------------------------------
            # MediaPipe image
            # -------------------------------------------------

            mp_image = mp.Image(
                image_format=mp.ImageFormat.SRGB,
                data=rgb_frame
            )

            # -------------------------------------------------
            # Timestamp
            # -------------------------------------------------

            timestamp_ms = int(
                (frame_count - 1) * 1000 / fps
            )

            if timestamp_ms <= last_timestamp_ms:
                timestamp_ms = last_timestamp_ms + 1

            last_timestamp_ms = timestamp_ms

            # -------------------------------------------------
            # Pose detection
            # -------------------------------------------------

            result = landmarker.detect_for_video(
                mp_image,
                timestamp_ms
            )

            # -------------------------------------------------
            # No pose
            # -------------------------------------------------

            if not result.pose_landmarks:
                continue

            if len(result.pose_landmarks) == 0:
                continue

            detected_frames += 1

            # -------------------------------------------------
            # First person
            # -------------------------------------------------

            landmarks = result.pose_landmarks[0]

            # =================================================
            # RIGHT SIDE
            # =================================================

            rs = landmarks[PoseLandmark.RIGHT_SHOULDER]
            re = landmarks[PoseLandmark.RIGHT_ELBOW]
            rw = landmarks[PoseLandmark.RIGHT_WRIST]

            rh = landmarks[PoseLandmark.RIGHT_HIP]
            rk = landmarks[PoseLandmark.RIGHT_KNEE]
            ra = landmarks[PoseLandmark.RIGHT_ANKLE]

            # =================================================
            # LEFT SIDE
            # =================================================

            ls = landmarks[PoseLandmark.LEFT_SHOULDER]
            le = landmarks[PoseLandmark.LEFT_ELBOW]
            lw = landmarks[PoseLandmark.LEFT_WRIST]

            lh = landmarks[PoseLandmark.LEFT_HIP]
            lk = landmarks[PoseLandmark.LEFT_KNEE]
            la = landmarks[PoseLandmark.LEFT_ANKLE]

            # =================================================
            # Convert to 2D points
            # =================================================

            right_shoulder = point(rs)
            right_elbow = point(re)
            right_wrist = point(rw)

            right_hip = point(rh)
            right_knee = point(rk)
            right_ankle = point(ra)

            left_shoulder = point(ls)
            left_elbow = point(le)
            left_wrist = point(lw)

            left_hip = point(lh)
            left_knee = point(lk)
            left_ankle = point(la)

            # =================================================
            # Joint angles
            # =================================================

            right_elbow_angle = calculate_angle(
                right_shoulder,
                right_elbow,
                right_wrist
            )

            left_elbow_angle = calculate_angle(
                left_shoulder,
                left_elbow,
                left_wrist
            )

            right_knee_angle = calculate_angle(
                right_hip,
                right_knee,
                right_ankle
            )

            left_knee_angle = calculate_angle(
                left_hip,
                left_knee,
                left_ankle
            )

            right_hip_angle = calculate_angle(
                right_shoulder,
                right_hip,
                right_knee
            )

            left_hip_angle = calculate_angle(
                left_shoulder,
                left_hip,
                left_knee
            )

            # =================================================
            # Store frame
            # =================================================

            frame_data.append({

                "frame": frame_count,

                "timestamp_ms": timestamp_ms,

                "timestamp_seconds": round(
                    timestamp_ms / 1000,
                    3
                ),

                # -----------------------------
                # Right landmarks
                # -----------------------------

                "right_shoulder": {
                    "x": round(rs.x, 5),
                    "y": round(rs.y, 5),
                    "z": round(rs.z, 5),
                    "visibility": round(
                        rs.visibility, 4
                    )
                },

                "right_elbow": {
                    "x": round(re.x, 5),
                    "y": round(re.y, 5),
                    "z": round(re.z, 5),
                    "visibility": round(
                        re.visibility, 4
                    )
                },

                "right_wrist": {
                    "x": round(rw.x, 5),
                    "y": round(rw.y, 5),
                    "z": round(rw.z, 5),
                    "visibility": round(
                        rw.visibility, 4
                    )
                },

                "right_hip": {
                    "x": round(rh.x, 5),
                    "y": round(rh.y, 5),
                    "z": round(rh.z, 5),
                    "visibility": round(
                        rh.visibility, 4
                    )
                },

                "right_knee": {
                    "x": round(rk.x, 5),
                    "y": round(rk.y, 5),
                    "z": round(rk.z, 5),
                    "visibility": round(
                        rk.visibility, 4
                    )
                },

                "right_ankle": {
                    "x": round(ra.x, 5),
                    "y": round(ra.y, 5),
                    "z": round(ra.z, 5),
                    "visibility": round(
                        ra.visibility, 4
                    )
                },

                # -----------------------------
                # Left landmarks
                # -----------------------------

                "left_shoulder": {
                    "x": round(ls.x, 5),
                    "y": round(ls.y, 5),
                    "z": round(ls.z, 5),
                    "visibility": round(
                        ls.visibility, 4
                    )
                },

                "left_elbow": {
                    "x": round(le.x, 5),
                    "y": round(le.y, 5),
                    "z": round(le.z, 5),
                    "visibility": round(
                        le.visibility, 4
                    )
                },

                "left_wrist": {
                    "x": round(lw.x, 5),
                    "y": round(lw.y, 5),
                    "z": round(lw.z, 5),
                    "visibility": round(
                        lw.visibility, 4
                    )
                },

                "left_hip": {
                    "x": round(lh.x, 5),
                    "y": round(lh.y, 5),
                    "z": round(lh.z, 5),
                    "visibility": round(
                        lh.visibility, 4
                    )
                },

                "left_knee": {
                    "x": round(lk.x, 5),
                    "y": round(lk.y, 5),
                    "z": round(lk.z, 5),
                    "visibility": round(
                        lk.visibility, 4
                    )
                },

                "left_ankle": {
                    "x": round(la.x, 5),
                    "y": round(la.y, 5),
                    "z": round(la.z, 5),
                    "visibility": round(
                        la.visibility, 4
                    )
                },

                # -----------------------------
                # Angles
                # -----------------------------

                "right_elbow_angle": right_elbow_angle,

                "left_elbow_angle": left_elbow_angle,

                "right_knee_angle": right_knee_angle,

                "left_knee_angle": left_knee_angle,

                "right_hip_angle": right_hip_angle,

                "left_hip_angle": left_hip_angle,
            })

    # -----------------------------------------------------
    # Release video
    # -----------------------------------------------------

    cap.release()

    # -----------------------------------------------------
    # No pose
    # -----------------------------------------------------

    if detected_frames == 0:

        return {
            "status": "no_pose_detected",
            "frames": frame_count,
            "detected_frames": 0,
            "pose_detection_rate": 0,
            "frame_data": []
        }

    # -----------------------------------------------------
    # Calculate averages
    # -----------------------------------------------------

    right_knee_angles = [
        x["right_knee_angle"]
        for x in frame_data
    ]

    right_hip_angles = [
        x["right_hip_angle"]
        for x in frame_data
    ]

    right_elbow_angles = [
        x["right_elbow_angle"]
        for x in frame_data
    ]

    # -----------------------------------------------------
    # Final result
    # -----------------------------------------------------

    return {

        "status": "analysis_complete",

        "frames": frame_count,

        "detected_frames": detected_frames,

        "pose_detection_rate": round(
            detected_frames / frame_count * 100,
            2
        ),

        "average_knee_angle": round(
            sum(right_knee_angles)
            / len(right_knee_angles),
            2
        ),

        "average_hip_angle": round(
            sum(right_hip_angles)
            / len(right_hip_angles),
            2
        ),

        "average_elbow_angle": round(
            sum(right_elbow_angles)
            / len(right_elbow_angles),
            2
        ),

        "frame_data": frame_data
    }