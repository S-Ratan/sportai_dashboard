import cv2
import math
from pathlib import Path

import mediapipe as mp


mp_pose = mp.solutions.pose

# Process one frame out of every three at a fixed, inference-friendly size.
FRAME_SIZE = (640, 360)
FRAME_SKIP = 3


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

    # -----------------------------------------------------
    # Frame-by-frame data
    # -----------------------------------------------------

    frame_data = []

    # -----------------------------------------------------
    # MediaPipe configuration. model_complexity=1 selects the balanced model,
    # avoiding the cost of the heavy pose model.
    # -----------------------------------------------------

    with mp_pose.Pose(
        static_image_mode=False,
        model_complexity=1,
        smooth_landmarks=True,
        enable_segmentation=False,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    ) as pose:

        while True:

            success, frame = cap.read()

            if not success:
                break

            frame_count += 1

            # Keep the first frame in each group so frame numbers and
            # timestamps continue to reference the original video.
            if (frame_count - 1) % FRAME_SKIP != 0:
                continue

            processed_frames += 1

            frame = cv2.resize(
                frame,
                FRAME_SIZE,
                interpolation=cv2.INTER_AREA,
            )

            # -------------------------------------------------
            # BGR -> RGB
            # -------------------------------------------------

            rgb_frame = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2RGB
            )

            timestamp_ms = int(
                (frame_count - 1) * 1000 / fps
            )

            # -------------------------------------------------
            # Pose detection
            # -------------------------------------------------

            result = pose.process(rgb_frame)

            # -------------------------------------------------
            # No pose
            # -------------------------------------------------

            if not result.pose_landmarks:
                continue

            detected_frames += 1

            # -------------------------------------------------
            # First person
            # -------------------------------------------------

            landmarks = result.pose_landmarks.landmark

            # =================================================
            # RIGHT SIDE
            # =================================================

            rs = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER]
            re = landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW]
            rw = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST]

            rh = landmarks[mp_pose.PoseLandmark.RIGHT_HIP]
            rk = landmarks[mp_pose.PoseLandmark.RIGHT_KNEE]
            ra = landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE]
            rf = landmarks[mp_pose.PoseLandmark.RIGHT_FOOT_INDEX]

            # =================================================
            # LEFT SIDE
            # =================================================

            ls = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
            le = landmarks[mp_pose.PoseLandmark.LEFT_ELBOW]
            lw = landmarks[mp_pose.PoseLandmark.LEFT_WRIST]

            lh = landmarks[mp_pose.PoseLandmark.LEFT_HIP]
            lk = landmarks[mp_pose.PoseLandmark.LEFT_KNEE]
            la = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE]
            lf = landmarks[mp_pose.PoseLandmark.LEFT_FOOT_INDEX]

            # =================================================
            # Convert to 2D points
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

            right_ankle_angle = calculate_angle(
                right_knee,
                right_ankle,
                right_foot
            )

            left_ankle_angle = calculate_angle(
                left_knee,
                left_ankle,
                left_foot
            )

            right_shoulder_angle = calculate_angle(
                right_elbow,
                right_shoulder,
                right_hip
            )

            left_shoulder_angle = calculate_angle(
                left_elbow,
                left_shoulder,
                left_hip
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

                "right_foot": {
                    "x": round(rf.x, 5),
                    "y": round(rf.y, 5),
                    "z": round(rf.z, 5),
                    "visibility": round(rf.visibility, 4)
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

                "left_foot": {
                    "x": round(lf.x, 5),
                    "y": round(lf.y, 5),
                    "z": round(lf.z, 5),
                    "visibility": round(lf.visibility, 4)
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

                "right_ankle_angle": right_ankle_angle,

                "left_ankle_angle": left_ankle_angle,

                "right_shoulder_angle": right_shoulder_angle,

                "left_shoulder_angle": left_shoulder_angle,
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
            detected_frames / processed_frames * 100,
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
