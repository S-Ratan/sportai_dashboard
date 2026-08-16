"""
Unit tests for the Biomechanical Calculation Service.

Tests the new ROM, angular velocity, and aggregation functions
without modifying or testing existing functionality.
"""

import sys
from pathlib import Path

# Add backend app to path
backend_path = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(backend_path))

from app.services.biomechanics_service import (
    calculate_knee_rom,
    calculate_hip_rom,
    calculate_trunk_angles,
    calculate_angular_velocity,
    aggregate_biomechanics,
    build_biomechanics_chart,
    is_valid_angle,
    clean_angle,
)


# =========================================================
# Test Helper Functions
# =========================================================

def test_is_valid_angle():
    """Test the is_valid_angle helper function."""
    
    # Valid angles
    assert is_valid_angle(20.0) == True
    assert is_valid_angle(90.0) == True
    assert is_valid_angle(180.0) == True
    assert is_valid_angle(120.5) == True
    
    # Invalid angles
    assert is_valid_angle(19.9) == False
    assert is_valid_angle(180.1) == False
    assert is_valid_angle(None) == False
    assert is_valid_angle(-45.0) == False
    
    print("✓ test_is_valid_angle passed")


def test_clean_angle():
    """Test the clean_angle helper function."""
    
    # Valid angle
    result = clean_angle(120.5)
    assert result == 120.5
    
    # Invalid angle - returns fallback
    result = clean_angle(15.0, fallback=90.0)
    assert result == 90.0
    
    # Invalid angle - no fallback
    result = clean_angle(15.0)
    assert result is None
    
    # None input
    result = clean_angle(None, fallback=100.0)
    assert result == 100.0
    
    print("✓ test_clean_angle passed")


# =========================================================
# Test ROM Calculations
# =========================================================

def test_calculate_knee_rom_valid_data():
    """Test knee ROM calculation with valid data."""
    
    angles = [80.0, 85.0, 90.0, 95.0, 100.0, 120.0, 110.0]
    result = calculate_knee_rom(angles)
    
    assert result is not None
    assert result["min_angle"] == 80.0
    assert result["max_angle"] == 120.0
    assert result["range_of_motion"] == 40.0
    assert "avg_angle" in result
    
    print("✓ test_calculate_knee_rom_valid_data passed")


def test_calculate_knee_rom_empty():
    """Test knee ROM calculation with empty data."""
    
    result = calculate_knee_rom([])
    assert result is None
    
    print("✓ test_calculate_knee_rom_empty passed")


def test_calculate_knee_rom_none_values():
    """Test knee ROM calculation with None values."""
    
    angles = [None, None, None]
    result = calculate_knee_rom(angles)
    assert result is None
    
    print("✓ test_calculate_knee_rom_none_values passed")


def test_calculate_knee_rom_mixed_valid_invalid():
    """Test knee ROM with mixed valid/invalid values."""
    
    angles = [80.0, None, 90.0, 15.0, 100.0, 200.0, 110.0]
    result = calculate_knee_rom(angles)
    
    # Should only use: 80, 90, 100, 110
    assert result is not None
    assert result["min_angle"] == 80.0
    assert result["max_angle"] == 110.0
    assert result["range_of_motion"] == 30.0
    
    print("✓ test_calculate_knee_rom_mixed_valid_invalid passed")


def test_calculate_hip_rom_valid_data():
    """Test hip ROM calculation with valid data."""
    
    angles = [70.0, 75.0, 80.0, 85.0, 90.0, 100.0]
    result = calculate_hip_rom(angles)
    
    assert result is not None
    assert result["min_angle"] == 70.0
    assert result["max_angle"] == 100.0
    assert result["range_of_motion"] == 30.0
    
    print("✓ test_calculate_hip_rom_valid_data passed")


def test_calculate_hip_rom_single_angle():
    """Test hip ROM calculation with single angle (no ROM)."""
    
    angles = [85.0]
    result = calculate_hip_rom(angles)
    
    assert result is not None
    assert result["min_angle"] == 85.0
    assert result["max_angle"] == 85.0
    assert result["range_of_motion"] == 0.0
    
    print("✓ test_calculate_hip_rom_single_angle passed")


# =========================================================
# Test Trunk Angle Analysis
# =========================================================

def test_calculate_trunk_angles_valid_data():
    """Test trunk angle analysis with valid data."""
    
    trunk_tilts = [5.0, 8.0, 12.0, 15.0, 18.0, 20.0, 16.0, 10.0]
    result = calculate_trunk_angles(trunk_tilts)
    
    assert result is not None
    assert result["min_angle"] == 5.0
    assert result["max_angle"] == 20.0
    assert result["range_of_motion"] == 15.0
    assert "avg_angle" in result
    
    print("✓ test_calculate_trunk_angles_valid_data passed")


def test_calculate_trunk_angles_empty():
    """Test trunk angle analysis with empty data."""
    
    result = calculate_trunk_angles([])
    assert result is None
    
    print("✓ test_calculate_trunk_angles_empty passed")


def test_calculate_trunk_angles_invalid_range():
    """Test trunk angle analysis with invalid range (out of bounds)."""
    
    # Trunk tilts should be 0-90 degrees
    trunk_tilts = [95.0, 100.0, 150.0]
    result = calculate_trunk_angles(trunk_tilts)
    
    assert result is None
    
    print("✓ test_calculate_trunk_angles_invalid_range passed")


def test_calculate_trunk_angles_mixed():
    """Test trunk angle analysis with mixed valid/invalid values."""
    
    trunk_tilts = [5.0, 95.0, 12.0, None, 20.0, 150.0, 15.0]
    result = calculate_trunk_angles(trunk_tilts)
    
    # Should only use: 5, 12, 20, 15
    assert result is not None
    assert result["min_angle"] == 5.0
    assert result["max_angle"] == 20.0
    
    print("✓ test_calculate_trunk_angles_mixed passed")


# =========================================================
# Test Angular Velocity
# =========================================================

def test_calculate_angular_velocity_steady():
    """Test angular velocity with steady movement."""
    
    # Angles changing by 5 degrees each frame
    angles = [90.0, 95.0, 100.0, 105.0, 110.0]
    result = calculate_angular_velocity(angles)
    
    assert result is not None
    assert result == 5.0  # 5 degrees per frame
    
    print("✓ test_calculate_angular_velocity_steady passed")


def test_calculate_angular_velocity_variable():
    """Test angular velocity with variable movement."""
    
    angles = [90.0, 92.0, 97.0, 100.0, 99.0, 105.0]
    result = calculate_angular_velocity(angles)
    
    assert result is not None
    # Changes: 2, 5, 3, 1, 6 -> avg = 17/5 = 3.4
    assert result == 3.4
    
    print("✓ test_calculate_angular_velocity_variable passed")


def test_calculate_angular_velocity_insufficient_data():
    """Test angular velocity with insufficient data."""
    
    angles = [90.0]
    result = calculate_angular_velocity(angles)
    
    assert result is None
    
    print("✓ test_calculate_angular_velocity_insufficient_data passed")


def test_calculate_angular_velocity_empty():
    """Test angular velocity with empty data."""
    
    result = calculate_angular_velocity([])
    assert result is None
    
    print("✓ test_calculate_angular_velocity_empty passed")


def test_calculate_angular_velocity_with_invalid_angles():
    """Test angular velocity filtering out invalid angles."""
    
    angles = [90.0, None, 95.0, 15.0, 100.0, 200.0, 105.0]
    result = calculate_angular_velocity(angles)
    
    # Valid angles: 90, 95, 100, 105
    # Changes: 5, 5, 5 -> avg = 5.0
    assert result is not None
    assert result == 5.0
    
    print("✓ test_calculate_angular_velocity_with_invalid_angles passed")


# =========================================================
# Test Aggregation
# =========================================================

def test_aggregate_biomechanics_empty():
    """Test aggregation with empty data."""
    
    result = aggregate_biomechanics([])
    assert result is None
    
    print("✓ test_aggregate_biomechanics_empty passed")


def test_aggregate_biomechanics_minimal():
    """Test aggregation with minimal valid data."""
    
    frame = {
        "left_knee_angle": 85.0,
        "right_knee_angle": 87.0,
        "left_hip_angle": 95.0,
        "right_hip_angle": 93.0,
        "trunk_tilt": 10.0,
        "knee_asymmetry": 2.0,
        "hip_asymmetry": 2.0,
        "elbow_asymmetry": None,
    }
    
    result = aggregate_biomechanics([frame])
    
    assert result is not None
    assert "left_knee" in result
    assert "right_knee" in result
    assert "left_hip" in result
    assert "right_hip" in result
    assert "trunk" in result
    assert "asymmetry_summary" in result
    
    print("✓ test_aggregate_biomechanics_minimal passed")


def test_aggregate_biomechanics_comprehensive():
    """Test aggregation with comprehensive data."""
    
    frames = [
        {
            "left_knee_angle": 85.0,
            "right_knee_angle": 87.0,
            "left_hip_angle": 95.0,
            "right_hip_angle": 93.0,
            "trunk_tilt": 10.0,
            "knee_asymmetry": 2.0,
            "hip_asymmetry": 2.0,
            "elbow_asymmetry": 3.0,
        },
        {
            "left_knee_angle": 90.0,
            "right_knee_angle": 92.0,
            "left_hip_angle": 98.0,
            "right_hip_angle": 96.0,
            "trunk_tilt": 12.0,
            "knee_asymmetry": 2.0,
            "hip_asymmetry": 2.0,
            "elbow_asymmetry": 3.5,
        },
        {
            "left_knee_angle": 95.0,
            "right_knee_angle": 97.0,
            "left_hip_angle": 100.0,
            "right_hip_angle": 99.0,
            "trunk_tilt": 14.0,
            "knee_asymmetry": 2.0,
            "hip_asymmetry": 1.0,
            "elbow_asymmetry": 3.2,
        },
    ]
    
    result = aggregate_biomechanics(frames)
    
    assert result is not None
    
    # Check left knee
    assert result["left_knee"]["min_angle"] == 85.0
    assert result["left_knee"]["max_angle"] == 95.0
    assert result["left_knee"]["range_of_motion"] == 10.0
    assert "avg_angular_velocity" in result["left_knee"]
    
    # Check right knee
    assert result["right_knee"]["min_angle"] == 87.0
    assert result["right_knee"]["max_angle"] == 97.0
    assert result["right_knee"]["range_of_motion"] == 10.0
    
    # Check trunk
    assert result["trunk"]["min_angle"] == 10.0
    assert result["trunk"]["max_angle"] == 14.0
    
    # Check asymmetry summary
    assert "avg_knee_asymmetry" in result["asymmetry_summary"]
    assert "avg_hip_asymmetry" in result["asymmetry_summary"]
    assert "avg_elbow_asymmetry" in result["asymmetry_summary"]
    
    # Verify asymmetry averages
    assert result["asymmetry_summary"]["avg_knee_asymmetry"] == 2.0
    assert result["asymmetry_summary"]["avg_hip_asymmetry"] == 1.67  # (2+2+1)/3
    assert result["asymmetry_summary"]["avg_elbow_asymmetry"] == 3.23  # (3+3.5+3.2)/3
    
    print("✓ test_aggregate_biomechanics_comprehensive passed")


def test_biomechanics_chart_contains_four_measured_joint_groups():
    summary = {
        "left_knee": {"avg_angle": 90.0}, "right_knee": {"avg_angle": 108.0},
        "left_hip": {"avg_angle": 72.0}, "right_hip": {"avg_angle": 81.0},
        "left_ankle": {"avg_angle": 99.0}, "right_ankle": {"avg_angle": 117.0},
        "left_shoulder": {"avg_angle": 126.0}, "right_shoulder": {"avg_angle": 144.0},
    }
    chart = build_biomechanics_chart(summary)

    assert list(chart) == ["knee", "hip", "ankle", "shoulder"]
    assert chart["knee"] == {"left": 50.0, "right": 60.0}
    assert chart["hip"] == {"left": 40.0, "right": 45.0}
    assert chart["ankle"] == {"left": 55.0, "right": 65.0}
    assert chart["shoulder"] == {"left": 70.0, "right": 80.0}


def test_aggregate_biomechanics_missing_fields():
    """Test aggregation when some fields are missing."""
    
    frames = [
        {
            "left_knee_angle": 85.0,
            "right_knee_angle": 87.0,
            # Missing hip and trunk
            "knee_asymmetry": 2.0,
        },
        {
            "left_knee_angle": 90.0,
            "right_knee_angle": 92.0,
            "left_hip_angle": 95.0,
            # Partial data
            "knee_asymmetry": 2.0,
        },
    ]
    
    result = aggregate_biomechanics(frames)
    
    assert result is not None
    # Left knee should have data
    assert "left_knee" in result
    assert result["left_knee"]["min_angle"] == 85.0
    
    # Hip should have partial data
    assert "left_hip" in result
    
    print("✓ test_aggregate_biomechanics_missing_fields passed")


def test_aggregate_biomechanics_all_invalid():
    """Test aggregation when all data is invalid."""
    
    frames = [
        {
            "left_knee_angle": None,
            "right_knee_angle": None,
            "left_hip_angle": None,
            "right_hip_angle": None,
            "trunk_tilt": None,
            "knee_asymmetry": None,
            "hip_asymmetry": None,
            "elbow_asymmetry": None,
        },
        {
            "left_knee_angle": 15.0,  # Invalid
            "right_knee_angle": 200.0,  # Invalid
            "left_hip_angle": None,
            "right_hip_angle": None,
            "trunk_tilt": 95.0,  # Invalid (>90)
            "knee_asymmetry": None,
            "hip_asymmetry": None,
            "elbow_asymmetry": None,
        },
    ]
    
    result = aggregate_biomechanics(frames)
    
    assert result is not None
    # All joints should be empty or have minimal data
    assert result["left_knee"] == {}
    assert result["asymmetry_summary"] == {}
    
    print("✓ test_aggregate_biomechanics_all_invalid passed")


# =========================================================
# Main Test Runner
# =========================================================

if __name__ == "__main__":
    print("\n" + "="*60)
    print("Testing Biomechanical Calculation Service")
    print("="*60 + "\n")
    
    # Test helper functions
    print("Testing Helper Functions:")
    test_is_valid_angle()
    test_clean_angle()
    
    # Test ROM calculations
    print("\nTesting ROM Calculations:")
    test_calculate_knee_rom_valid_data()
    test_calculate_knee_rom_empty()
    test_calculate_knee_rom_none_values()
    test_calculate_knee_rom_mixed_valid_invalid()
    test_calculate_hip_rom_valid_data()
    test_calculate_hip_rom_single_angle()
    
    # Test trunk angle analysis
    print("\nTesting Trunk Angle Analysis:")
    test_calculate_trunk_angles_valid_data()
    test_calculate_trunk_angles_empty()
    test_calculate_trunk_angles_invalid_range()
    test_calculate_trunk_angles_mixed()
    
    # Test angular velocity
    print("\nTesting Angular Velocity:")
    test_calculate_angular_velocity_steady()
    test_calculate_angular_velocity_variable()
    test_calculate_angular_velocity_insufficient_data()
    test_calculate_angular_velocity_empty()
    test_calculate_angular_velocity_with_invalid_angles()
    
    # Test aggregation
    print("\nTesting Aggregation:")
    test_aggregate_biomechanics_empty()
    test_aggregate_biomechanics_minimal()
    test_aggregate_biomechanics_comprehensive()
    test_aggregate_biomechanics_missing_fields()
    test_aggregate_biomechanics_all_invalid()
    
    print("\n" + "="*60)
    print("✅ All tests passed!")
    print("="*60 + "\n")
