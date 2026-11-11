import os
from pathlib import Path
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_detect_image_upload_and_inference():
    sample_img_path = Path("ml/inference/samples/road_pothole_severe.jpg")
    assert sample_img_path.exists(), "Sample test image must exist"

    with open(sample_img_path, "rb") as f:
        response = client.post(
            "/api/v1/detect",
            files={"file": ("road_pothole_severe.jpg", f, "image/jpeg")},
            data={"location_notes": "Highway 101 Mile 42"}
        )

    assert response.status_code == 200, f"Error: {response.text}"
    data = response.json()

    # Validate schema
    assert "id" in data
    assert data["original_filename"] == "road_pothole_severe.jpg"
    assert data["image_width"] > 0
    assert data["image_height"] > 0
    assert data["severity_level"] in ["Low", "Medium", "High"]
    assert 0.0 <= data["severity_score"] <= 100.0
    assert data["inference_time_ms"] > 0.0
    assert "annotated_image_url" in data
    assert "damages" in data
    assert data["location_notes"] == "Highway 101 Mile 42"

    # Test retrieve single detection
    det_id = data["id"]
    get_res = client.get(f"/api/v1/detect/{det_id}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == det_id


def test_invalid_file_extension():
    fake_file = b"not an image content"
    response = client.post(
        "/api/v1/detect",
        files={"file": ("malicious.exe", fake_file, "application/octet-stream")}
    )
    assert response.status_code == 400
    assert "Unsupported file format" in response.json()["detail"]


def test_history_and_analytics_endpoints():
    # 1. History list
    res_hist = client.get("/api/v1/history?page=1&limit=10")
    assert res_hist.status_code == 200
    hist_data = res_hist.json()
    assert "items" in hist_data
    assert "total" in hist_data
    assert hist_data["total"] >= 1

    # 2. Analytics overview
    res_analytics = client.get("/api/v1/analytics/overview")
    assert res_analytics.status_code == 200
    analytics_data = res_analytics.json()
    assert analytics_data["total_inspections"] >= 1
    assert "severity_breakdown" in analytics_data
    assert "damage_type_breakdown" in analytics_data

