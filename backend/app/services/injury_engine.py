def average(values):
    values = [v for v in values if v is not None]

    if not values:
        return None

    return sum(values) / len(values)


def calculate_injury_risk(frame_data):
    """
    Calculate a basic biomechanics-based injury risk score.

    This is a screening indicator, NOT a medical diagnosis.
    """

    if not frame_data:
        return {
            "risk_score": 0,
            "risk_level": "unknown",
            "factors": []
        }

    knee_asymmetry = average(
        [f.get("knee_asymmetry") for f in frame_data]
    )

    hip_asymmetry = average(
        [f.get("hip_asymmetry") for f in frame_data]
    )

    elbow_asymmetry = average(
        [f.get("elbow_asymmetry") for f in frame_data]
    )

    trunk_tilt = average(
        [f.get("trunk_tilt") for f in frame_data]
    )

    shoulder_symmetry = average(
        [f.get("shoulder_symmetry") for f in frame_data]
    )

    score = 0
    factors = []

    # ----------------------------------------
    # Knee asymmetry
    # ----------------------------------------

    if knee_asymmetry is not None:

        if knee_asymmetry > 15:
            score += 30
            factors.append(
                "High knee asymmetry"
            )

        elif knee_asymmetry > 8:
            score += 15
            factors.append(
                "Moderate knee asymmetry"
            )

    # ----------------------------------------
    # Hip asymmetry
    # ----------------------------------------

    if hip_asymmetry is not None:

        if hip_asymmetry > 15:
            score += 20
            factors.append(
                "High hip asymmetry"
            )

        elif hip_asymmetry > 8:
            score += 10
            factors.append(
                "Moderate hip asymmetry"
            )

    # ----------------------------------------
    # Elbow asymmetry
    # ----------------------------------------

    if elbow_asymmetry is not None:

        if elbow_asymmetry > 30:
            score += 20
            factors.append(
                "High elbow asymmetry"
            )

        elif elbow_asymmetry > 15:
            score += 10
            factors.append(
                "Moderate elbow asymmetry"
            )

    # ----------------------------------------
    # Trunk tilt
    # ----------------------------------------

    if trunk_tilt is not None:

        if trunk_tilt > 15:
            score += 20
            factors.append(
                "Excessive trunk tilt"
            )

        elif trunk_tilt > 8:
            score += 10
            factors.append(
                "Moderate trunk tilt"
            )

    # ----------------------------------------
    # Shoulder symmetry
    # ----------------------------------------

    if shoulder_symmetry is not None:

        if shoulder_symmetry > 0.08:
            score += 10
            factors.append(
                "Shoulder asymmetry detected"
            )

        elif shoulder_symmetry > 0.04:
            score += 5
            factors.append(
                "Moderate shoulder asymmetry"
            )

    # ----------------------------------------
    # Limit score
    # ----------------------------------------

    score = min(score, 100)

    # ----------------------------------------
    # Risk level
    # ----------------------------------------

    if score >= 60:
        risk_level = "high"

    elif score >= 30:
        risk_level = "moderate"

    else:
        risk_level = "low"

    return {
        "risk_score": round(score, 2),
        "risk_level": risk_level,
        "factors": factors,

        "metrics": {
            "average_knee_asymmetry": round(
                knee_asymmetry, 2
            ) if knee_asymmetry is not None else None,

            "average_hip_asymmetry": round(
                hip_asymmetry, 2
            ) if hip_asymmetry is not None else None,

            "average_elbow_asymmetry": round(
                elbow_asymmetry, 2
            ) if elbow_asymmetry is not None else None,

            "average_trunk_tilt": round(
                trunk_tilt, 2
            ) if trunk_tilt is not None else None,

            "average_shoulder_symmetry": round(
                shoulder_symmetry, 4
            ) if shoulder_symmetry is not None else None,
        }
    }