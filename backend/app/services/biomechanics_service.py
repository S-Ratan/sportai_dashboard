import math


# =========================================================
# Utility
# =========================================================

def is_valid_angle(angle):
    """
    Check whether an angle is physically usable.
    """
    if angle is None:
        return False

    return 20 <= angle <= 180


def clean_angle(angle, fallback=None):
    """
    Remove obviously invalid/outlier angles.
    """
    if not is_valid_angle(angle):
        return fallback

    return round(angle, 2)


# =========================================================
# Asymmetry
# =========================================================

def calculate_asymmetry(right, left):
    """
    Absolute difference between left and right angles.
    """
    if right is None or left is None:
        return None

    return round(abs(right - left), 2)


# =========================================================
# Trunk Tilt
# =========================================================

def calculate_trunk_tilt(
    left_shoulder,
    right_shoulder,
    left_hip,
    right_hip
):
    """
    Calculate trunk tilt using the center of shoulders
    and center of hips.

    Result is an angle in degrees.
    """

    if not all([
        left_shoulder,
        right_shoulder,
        left_hip,
        right_hip
    ]):
        return None

    shoulder_x = (
        left_shoulder["x"] +
        right_shoulder["x"]
    ) / 2

    shoulder_y = (
        left_shoulder["y"] +
        right_shoulder["y"]
    ) / 2

    hip_x = (
        left_hip["x"] +
        right_hip["x"]
    ) / 2

    hip_y = (
        left_hip["y"] +
        right_hip["y"]
    ) / 2

    dx = shoulder_x - hip_x
    dy = shoulder_y - hip_y

    if dx == 0 and dy == 0:
        return 0.0

    angle = math.degrees(
        math.atan2(abs(dx), abs(dy))
    )

    return round(angle, 2)


# =========================================================
# Shoulder Symmetry
# =========================================================

def calculate_shoulder_symmetry(
    left_shoulder,
    right_shoulder
):
    """
    Difference between left and right shoulder height.

    Uses normalized MediaPipe Y coordinates.
    Smaller value = more symmetrical.
    """

    if not left_shoulder or not right_shoulder:
        return None

    return round(
        abs(
            left_shoulder["y"] -
            right_shoulder["y"]
        ),
        4
    )


# =========================================================
# Hip Alignment
# =========================================================

def calculate_hip_alignment(
    left_hip,
    right_hip
):
    """
    Difference between left and right hip height.

    Uses normalized MediaPipe Y coordinates.
    Smaller value = better alignment.
    """

    if not left_hip or not right_hip:
        return None

    return round(
        abs(
            left_hip["y"] -
            right_hip["y"]
        ),
        4
    )


# =========================================================
# Process One Frame
# =========================================================

def process_frame(frame):
    """
    Convert raw pose frame data into biomechanics metrics.
    """

    # -----------------------------------------------------
    # Angles
    # -----------------------------------------------------

    right_elbow = clean_angle(
        frame.get("right_elbow_angle")
    )

    left_elbow = clean_angle(
        frame.get("left_elbow_angle")
    )

    right_knee = clean_angle(
        frame.get("right_knee_angle")
    )

    left_knee = clean_angle(
        frame.get("left_knee_angle")
    )

    right_hip = clean_angle(
        frame.get("right_hip_angle")
    )

    left_hip = clean_angle(
        frame.get("left_hip_angle")
    )

    # -----------------------------------------------------
    # Biomechanics
    # -----------------------------------------------------

    trunk_tilt = calculate_trunk_tilt(
        frame.get("left_shoulder"),
        frame.get("right_shoulder"),
        frame.get("left_hip"),
        frame.get("right_hip")
    )

    shoulder_symmetry = calculate_shoulder_symmetry(
        frame.get("left_shoulder"),
        frame.get("right_shoulder")
    )

    hip_alignment = calculate_hip_alignment(
        frame.get("left_hip"),
        frame.get("right_hip")
    )

    # -----------------------------------------------------
    # Result
    # -----------------------------------------------------

    result = {

        "frame": frame.get("frame"),

        "timestamp_seconds": frame.get(
            "timestamp_seconds"
        ),

        # Angles
        "right_elbow_angle": right_elbow,
        "left_elbow_angle": left_elbow,

        "right_knee_angle": right_knee,
        "left_knee_angle": left_knee,

        "right_hip_angle": right_hip,
        "left_hip_angle": left_hip,

        # Asymmetry
        "elbow_asymmetry": calculate_asymmetry(
            right_elbow,
            left_elbow
        ),

        "knee_asymmetry": calculate_asymmetry(
            right_knee,
            left_knee
        ),

        "hip_asymmetry": calculate_asymmetry(
            right_hip,
            left_hip
        ),

        # Alignment
        "trunk_tilt": trunk_tilt,

        "shoulder_symmetry": shoulder_symmetry,

        "hip_alignment": hip_alignment,
    }

    return result