import math
from typing import Optional, Dict, List, Any


# =========================================================
# Utility
# =========================================================

def is_valid_angle(angle: Optional[float]) -> bool:
    """
    Check whether an angle is physically usable.
    """
    if angle is None:
        return False

    return 20 <= angle <= 180


def clean_angle(angle: Optional[float], fallback: Optional[float] = None) -> Optional[float]:
    """
    Remove obviously invalid/outlier angles.
    """
    if not is_valid_angle(angle):
        return fallback

    return round(angle, 2)


# =========================================================
# Asymmetry
# =========================================================

def calculate_asymmetry(right: Optional[float], left: Optional[float]) -> Optional[float]:
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
    left_shoulder: Optional[Dict[str, float]],
    right_shoulder: Optional[Dict[str, float]],
    left_hip: Optional[Dict[str, float]],
    right_hip: Optional[Dict[str, float]]
) -> Optional[float]:
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
    left_shoulder: Optional[Dict[str, float]],
    right_shoulder: Optional[Dict[str, float]]
) -> Optional[float]:
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
    left_hip: Optional[Dict[str, float]],
    right_hip: Optional[Dict[str, float]]
) -> Optional[float]:
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

def process_frame(frame: Dict[str, Any]) -> Dict[str, Any]:
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

    right_ankle = clean_angle(
        frame.get("right_ankle_angle")
    )

    left_ankle = clean_angle(
        frame.get("left_ankle_angle")
    )

    right_shoulder = clean_angle(
        frame.get("right_shoulder_angle")
    )

    left_shoulder = clean_angle(
        frame.get("left_shoulder_angle")
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

        "right_ankle_angle": right_ankle,
        "left_ankle_angle": left_ankle,

        "right_shoulder_angle": right_shoulder,
        "left_shoulder_angle": left_shoulder,

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


# =========================================================
# Range of Motion (ROM)
# =========================================================

def calculate_knee_rom(angles: List[Optional[float]]) -> Optional[Dict[str, float]]:
    """
    Calculate knee Range of Motion (ROM) statistics.
    
    Args:
        angles: List of knee angles (in degrees) across frames
        
    Returns:
        Dictionary with min_angle, max_angle, range, and average,
        or None if no valid angles
    """
    valid_angles = [a for a in angles if is_valid_angle(a)]
    
    if not valid_angles:
        return None
    
    min_angle = round(min(valid_angles), 2)
    max_angle = round(max(valid_angles), 2)
    avg_angle = round(sum(valid_angles) / len(valid_angles), 2)
    rom = round(max_angle - min_angle, 2)
    
    return {
        "min_angle": min_angle,
        "max_angle": max_angle,
        "avg_angle": avg_angle,
        "range_of_motion": rom
    }


def calculate_hip_rom(angles: List[Optional[float]]) -> Optional[Dict[str, float]]:
    """
    Calculate hip Range of Motion (ROM) statistics.
    
    Args:
        angles: List of hip angles (in degrees) across frames
        
    Returns:
        Dictionary with min_angle, max_angle, range, and average,
        or None if no valid angles
    """
    valid_angles = [a for a in angles if is_valid_angle(a)]
    
    if not valid_angles:
        return None
    
    min_angle = round(min(valid_angles), 2)
    max_angle = round(max(valid_angles), 2)
    avg_angle = round(sum(valid_angles) / len(valid_angles), 2)
    rom = round(max_angle - min_angle, 2)
    
    return {
        "min_angle": min_angle,
        "max_angle": max_angle,
        "avg_angle": avg_angle,
        "range_of_motion": rom
    }


# =========================================================
# Trunk Angle Analysis
# =========================================================

def calculate_trunk_angles(trunk_tilts: List[Optional[float]]) -> Optional[Dict[str, float]]:
    """
    Calculate detailed trunk angle statistics across all frames.
    
    Args:
        trunk_tilts: List of trunk tilt angles across frames
        
    Returns:
        Dictionary with min, max, average trunk angles and range,
        or None if no valid angles
    """
    valid_tilts = [t for t in trunk_tilts if t is not None and 0 <= t <= 90]
    
    if not valid_tilts:
        return None
    
    min_angle = round(min(valid_tilts), 2)
    max_angle = round(max(valid_tilts), 2)
    avg_angle = round(sum(valid_tilts) / len(valid_tilts), 2)
    rom = round(max_angle - min_angle, 2)
    
    return {
        "min_angle": min_angle,
        "max_angle": max_angle,
        "avg_angle": avg_angle,
        "range_of_motion": rom
    }


# =========================================================
# Angular Velocity (frame-to-frame change)
# =========================================================

def calculate_angular_velocity(angles: List[Optional[float]]) -> Optional[float]:
    """
    Calculate average angular velocity (frame-to-frame angular change).
    
    Angular velocity = average absolute angle change per frame (degrees/frame)
    
    Args:
        angles: List of angles (in degrees) across consecutive frames
        
    Returns:
        Average angular velocity in degrees/frame, or None if insufficient data
    """
    valid_angles = [a for a in angles if is_valid_angle(a)]
    
    if len(valid_angles) < 2:
        return None
    
    frame_changes = []
    for i in range(1, len(valid_angles)):
        change = abs(valid_angles[i] - valid_angles[i-1])
        frame_changes.append(change)
    
    if not frame_changes:
        return None
    
    avg_velocity = round(sum(frame_changes) / len(frame_changes), 2)
    return avg_velocity


# =========================================================
# Aggregate Biomechanics (ROM, Velocity, Asymmetry Summary)
# =========================================================

def aggregate_biomechanics(biomechanics_frames: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """
    Aggregate per-frame biomechanics data to compute ROM, angular velocity,
    and asymmetry summaries across all frames.
    
    This consumes the output of process_frame() for all frames and produces
    comprehensive biomechanical statistics.
    
    Args:
        biomechanics_frames: List of per-frame biomechanics dictionaries
                           (output from process_frame())
    
    Returns:
        Dictionary with aggregated biomechanics metrics:
        {
            "left_knee": { rom_stats, velocity },
            "right_knee": { rom_stats, velocity },
            "left_hip": { rom_stats, velocity },
            "right_hip": { rom_stats, velocity },
            "trunk": { rom_stats, velocity },
            "asymmetry_summary": {
                "avg_knee_asymmetry": float,
                "avg_hip_asymmetry": float,
                "avg_elbow_asymmetry": float
            }
        }
        
        Returns None if input is empty or invalid.
    """
    
    if not biomechanics_frames or len(biomechanics_frames) == 0:
        return None
    
    # Extract angle sequences for each joint
    left_knee_angles = [f.get("left_knee_angle") for f in biomechanics_frames]
    right_knee_angles = [f.get("right_knee_angle") for f in biomechanics_frames]
    
    left_hip_angles = [f.get("left_hip_angle") for f in biomechanics_frames]
    right_hip_angles = [f.get("right_hip_angle") for f in biomechanics_frames]

    left_ankle_angles = [f.get("left_ankle_angle") for f in biomechanics_frames]
    right_ankle_angles = [f.get("right_ankle_angle") for f in biomechanics_frames]

    left_shoulder_angles = [f.get("left_shoulder_angle") for f in biomechanics_frames]
    right_shoulder_angles = [f.get("right_shoulder_angle") for f in biomechanics_frames]
    
    trunk_tilts = [f.get("trunk_tilt") for f in biomechanics_frames]
    
    # Extract asymmetry values
    knee_asymmetries = [f.get("knee_asymmetry") for f in biomechanics_frames]
    hip_asymmetries = [f.get("hip_asymmetry") for f in biomechanics_frames]
    elbow_asymmetries = [f.get("elbow_asymmetry") for f in biomechanics_frames]
    
    # Calculate ROM and angular velocity for each joint
    left_knee_rom = calculate_knee_rom(left_knee_angles)
    right_knee_rom = calculate_knee_rom(right_knee_angles)
    
    left_hip_rom = calculate_hip_rom(left_hip_angles)
    right_hip_rom = calculate_hip_rom(right_hip_angles)

    left_ankle_rom = calculate_knee_rom(left_ankle_angles)
    right_ankle_rom = calculate_knee_rom(right_ankle_angles)

    left_shoulder_rom = calculate_knee_rom(left_shoulder_angles)
    right_shoulder_rom = calculate_knee_rom(right_shoulder_angles)
    
    trunk_analysis = calculate_trunk_angles(trunk_tilts)
    
    # Calculate angular velocities
    left_knee_velocity = calculate_angular_velocity(left_knee_angles)
    right_knee_velocity = calculate_angular_velocity(right_knee_angles)
    
    left_hip_velocity = calculate_angular_velocity(left_hip_angles)
    right_hip_velocity = calculate_angular_velocity(right_hip_angles)

    left_ankle_velocity = calculate_angular_velocity(left_ankle_angles)
    right_ankle_velocity = calculate_angular_velocity(right_ankle_angles)

    left_shoulder_velocity = calculate_angular_velocity(left_shoulder_angles)
    right_shoulder_velocity = calculate_angular_velocity(right_shoulder_angles)
    
    trunk_velocity = calculate_angular_velocity(trunk_tilts)
    
    # Calculate average asymmetries
    valid_knee_asymmetries = [a for a in knee_asymmetries if a is not None]
    valid_hip_asymmetries = [a for a in hip_asymmetries if a is not None]
    valid_elbow_asymmetries = [a for a in elbow_asymmetries if a is not None]
    
    avg_knee_asymmetry = round(
        sum(valid_knee_asymmetries) / len(valid_knee_asymmetries), 2
    ) if valid_knee_asymmetries else None
    
    avg_hip_asymmetry = round(
        sum(valid_hip_asymmetries) / len(valid_hip_asymmetries), 2
    ) if valid_hip_asymmetries else None
    
    avg_elbow_asymmetry = round(
        sum(valid_elbow_asymmetries) / len(valid_elbow_asymmetries), 2
    ) if valid_elbow_asymmetries else None
    
    # Build result
    result = {
        "left_knee": {},
        "right_knee": {},
        "left_hip": {},
        "right_hip": {},
        "left_ankle": {},
        "right_ankle": {},
        "left_shoulder": {},
        "right_shoulder": {},
        "trunk": {},
        "asymmetry_summary": {}
    }
    
    # Add left knee metrics
    if left_knee_rom:
        result["left_knee"].update(left_knee_rom)
    if left_knee_velocity is not None:
        result["left_knee"]["avg_angular_velocity"] = left_knee_velocity
    
    # Add right knee metrics
    if right_knee_rom:
        result["right_knee"].update(right_knee_rom)
    if right_knee_velocity is not None:
        result["right_knee"]["avg_angular_velocity"] = right_knee_velocity
    
    # Add left hip metrics
    if left_hip_rom:
        result["left_hip"].update(left_hip_rom)
    if left_hip_velocity is not None:
        result["left_hip"]["avg_angular_velocity"] = left_hip_velocity
    
    # Add right hip metrics
    if right_hip_rom:
        result["right_hip"].update(right_hip_rom)
    if right_hip_velocity is not None:
        result["right_hip"]["avg_angular_velocity"] = right_hip_velocity

    for side, joint_rom, velocity in (
        ("left_ankle", left_ankle_rom, left_ankle_velocity),
        ("right_ankle", right_ankle_rom, right_ankle_velocity),
        ("left_shoulder", left_shoulder_rom, left_shoulder_velocity),
        ("right_shoulder", right_shoulder_rom, right_shoulder_velocity),
    ):
        if joint_rom:
            result[side].update(joint_rom)
        if velocity is not None:
            result[side]["avg_angular_velocity"] = velocity
    
    # Add trunk metrics
    if trunk_analysis:
        result["trunk"].update(trunk_analysis)
    if trunk_velocity is not None:
        result["trunk"]["avg_angular_velocity"] = trunk_velocity
    
    # Add asymmetry summary
    if avg_knee_asymmetry is not None:
        result["asymmetry_summary"]["avg_knee_asymmetry"] = avg_knee_asymmetry
    if avg_hip_asymmetry is not None:
        result["asymmetry_summary"]["avg_hip_asymmetry"] = avg_hip_asymmetry
    if avg_elbow_asymmetry is not None:
        result["asymmetry_summary"]["avg_elbow_asymmetry"] = avg_elbow_asymmetry
    
    return result


def build_biomechanics_chart(summary: Optional[Dict[str, Any]]) -> Dict[str, Dict[str, Optional[float]]]:
    """Return normalized left/right joint-angle scores for the dashboard chart.

    The chart is intentionally a 0-100 representation of measured mean joint
    angles (0-180 degrees), not placeholder values. Raw degree measurements
    remain available in ``biomechanics_summary``.
    """
    summary = summary or {}

    def score(key: str) -> Optional[float]:
        angle = summary.get(key, {}).get("avg_angle")
        if not isinstance(angle, (int, float)):
            return None
        return round(max(0, min(angle, 180)) / 180 * 100, 2)

    return {
        "knee": {"left": score("left_knee"), "right": score("right_knee")},
        "hip": {"left": score("left_hip"), "right": score("right_hip")},
        "ankle": {"left": score("left_ankle"), "right": score("right_ankle")},
        "shoulder": {"left": score("left_shoulder"), "right": score("right_shoulder")},
    }
