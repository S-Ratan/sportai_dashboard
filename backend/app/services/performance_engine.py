def average(values):
    values = [v for v in values if v is not None]

    if not values:
        return None

    return sum(values) / len(values)


def calculate_performance(frame_data):
    """
    Calculate overall bowling performance score.

    Score is based on:
    - Trunk control
    - Elbow symmetry
    - Knee symmetry
    - Hip symmetry
    - Shoulder symmetry
    - Hip alignment
    """

    if not frame_data:
        return {
            "performance_score": 0,
            "metrics": {},
            "factors": []
        }

    elbow_asymmetry = []
    knee_asymmetry = []
    hip_asymmetry = []
    trunk_tilts = []
    shoulder_symmetry = []
    hip_alignment = []

    for frame in frame_data:

        if frame.get("elbow_asymmetry") is not None:
            elbow_asymmetry.append(
                frame["elbow_asymmetry"]
            )

        if frame.get("knee_asymmetry") is not None:
            knee_asymmetry.append(
                frame["knee_asymmetry"]
            )

        if frame.get("hip_asymmetry") is not None:
            hip_asymmetry.append(
                frame["hip_asymmetry"]
            )

        if frame.get("trunk_tilt") is not None:
            trunk_tilts.append(
                frame["trunk_tilt"]
            )

        if frame.get("shoulder_symmetry") is not None:
            shoulder_symmetry.append(
                frame["shoulder_symmetry"]
            )

        if frame.get("hip_alignment") is not None:
            hip_alignment.append(
                frame["hip_alignment"]
            )

    avg_elbow_asymmetry = average(elbow_asymmetry)
    avg_knee_asymmetry = average(knee_asymmetry)
    avg_hip_asymmetry = average(hip_asymmetry)
    avg_trunk = average(trunk_tilts)
    avg_shoulder = average(shoulder_symmetry)
    avg_hip_alignment = average(hip_alignment)

    # --------------------------------------------------
    # Start with perfect score
    # --------------------------------------------------

    score = 100
    factors = []

    # --------------------------------------------------
    # Elbow asymmetry
    # --------------------------------------------------

    if avg_elbow_asymmetry is not None:

        if avg_elbow_asymmetry > 40:
            score -= 25
            factors.append("High elbow asymmetry")

        elif avg_elbow_asymmetry > 25:
            score -= 15
            factors.append("Moderate elbow asymmetry")

        elif avg_elbow_asymmetry > 15:
            score -= 8
            factors.append("Mild elbow asymmetry")

    # --------------------------------------------------
    # Knee asymmetry
    # --------------------------------------------------

    if avg_knee_asymmetry is not None:

        if avg_knee_asymmetry > 15:
            score -= 20
            factors.append("High knee asymmetry")

        elif avg_knee_asymmetry > 8:
            score -= 10
            factors.append("Moderate knee asymmetry")

        elif avg_knee_asymmetry > 5:
            score -= 5
            factors.append("Mild knee asymmetry")

    # --------------------------------------------------
    # Hip asymmetry
    # --------------------------------------------------

    if avg_hip_asymmetry is not None:

        if avg_hip_asymmetry > 15:
            score -= 15
            factors.append("High hip asymmetry")

        elif avg_hip_asymmetry > 8:
            score -= 8
            factors.append("Moderate hip asymmetry")

        elif avg_hip_asymmetry > 5:
            score -= 4
            factors.append("Mild hip asymmetry")

    # --------------------------------------------------
    # Trunk tilt
    # --------------------------------------------------

    if avg_trunk is not None:

        if avg_trunk > 20:
            score -= 20
            factors.append("High trunk tilt")

        elif avg_trunk > 10:
            score -= 10
            factors.append("Moderate trunk tilt")

        elif avg_trunk > 5:
            score -= 5
            factors.append("Mild trunk tilt")

    # --------------------------------------------------
    # Shoulder symmetry
    # --------------------------------------------------

    if avg_shoulder is not None:

        if avg_shoulder > 0.05:
            score -= 10
            factors.append("Poor shoulder symmetry")

        elif avg_shoulder > 0.02:
            score -= 5
            factors.append("Moderate shoulder asymmetry")

    # --------------------------------------------------
    # Hip alignment
    # --------------------------------------------------

    if avg_hip_alignment is not None:

        if avg_hip_alignment > 0.05:
            score -= 10
            factors.append("Poor hip alignment")

        elif avg_hip_alignment > 0.02:
            score -= 5
            factors.append("Moderate hip alignment issue")

    # --------------------------------------------------
    # Clamp score
    # --------------------------------------------------

    score = max(0, min(score, 100))

    # --------------------------------------------------
    # Performance level
    # --------------------------------------------------

    if score >= 85:
        level = "Excellent"

    elif score >= 70:
        level = "Good"

    elif score >= 50:
        level = "Needs Improvement"

    else:
        level = "Poor"

    return {
        "performance_score": round(score, 2),
        "performance_level": level,

        "metrics": {
            "average_elbow_asymmetry": round(
                avg_elbow_asymmetry, 2
            ) if avg_elbow_asymmetry is not None else None,

            "average_knee_asymmetry": round(
                avg_knee_asymmetry, 2
            ) if avg_knee_asymmetry is not None else None,

            "average_hip_asymmetry": round(
                avg_hip_asymmetry, 2
            ) if avg_hip_asymmetry is not None else None,

            "average_trunk_tilt": round(
                avg_trunk, 2
            ) if avg_trunk is not None else None,

            "average_shoulder_symmetry": round(
                avg_shoulder, 4
            ) if avg_shoulder is not None else None,

            "average_hip_alignment": round(
                avg_hip_alignment, 4
            ) if avg_hip_alignment is not None else None,
        },

        "factors": factors
    }