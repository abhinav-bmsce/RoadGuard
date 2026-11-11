import pytest
from backend.app.services.severity_analyzer import SeverityAnalyzer


def test_severity_weights():
    assert SeverityAnalyzer.get_class_weight("D00_Longitudinal_Crack") == 1.0
    assert SeverityAnalyzer.get_class_weight("D10_Transverse_Crack") == 1.2
    assert SeverityAnalyzer.get_class_weight("D20_Alligator_Crack") == 2.2
    assert SeverityAnalyzer.get_class_weight("D40_Pothole") == 3.0


def test_instance_severity_calculation():
    # Hairline longitudinal crack: 640x640, box 100x40 (4,000 px out of 409,600 = ~0.00976)
    bbox = {"xmin": 100, "ymin": 100, "xmax": 200, "ymax": 140}
    area_ratio, score, tag = SeverityAnalyzer.calculate_instance_severity(
        bbox=bbox,
        confidence=0.85,
        class_name="D00_Longitudinal_Crack",
        image_width=640,
        image_height=640
    )
    assert area_ratio > 0.0
    assert 0.0 <= score <= 100.0
    assert tag in ["Low", "Medium", "High"]
    assert tag == "Low"  # Hairline crack must be Low severity

    # Large Pothole: 640x640, box 300x250 (75,000 px out of 409,600 = ~18.3% of image)
    large_pothole_bbox = {"xmin": 100, "ymin": 100, "xmax": 400, "ymax": 350}
    p_ratio, p_score, p_tag = SeverityAnalyzer.calculate_instance_severity(
        bbox=large_pothole_bbox,
        confidence=0.92,
        class_name="D40_Pothole",
        image_width=640,
        image_height=640
    )
    assert p_ratio > 0.10
    assert p_tag in ["Medium", "High"]
    assert p_score > score  # Pothole must have significantly higher score than hairline crack


def test_cumulative_frame_severity():
    # Empty detections -> Low severity 0.0 score
    score, level = SeverityAnalyzer.calculate_frame_severity([])
    assert score == 0.0
    assert level == "Low"

    # Frame with high severity pothole
    instances = [
        {"instance_severity": 75.0, "severity_tag": "High"},
        {"instance_severity": 15.0, "severity_tag": "Low"},
    ]
    frame_score, frame_level = SeverityAnalyzer.calculate_frame_severity(instances)
    assert frame_score > 45.0
    assert frame_level in ["Medium", "High"]

