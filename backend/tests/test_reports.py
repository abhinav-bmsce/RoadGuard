from pathlib import Path
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_pdf_report_generation():
    # 1. Trigger detection to have an ID
    sample_img_path = Path("ml/inference/samples/road_pothole_severe.jpg")
    with open(sample_img_path, "rb") as f:
        det_res = client.post(
            "/api/v1/detect",
            files={"file": ("road_pothole_severe.jpg", f, "image/jpeg")},
            data={"location_notes": "Bridge Inspection Span 4"}
        )
    assert det_res.status_code == 200
    det_id = det_res.json()["id"]

    # 2. Test generate report endpoint
    gen_res = client.post(
        f"/api/v1/reports/{det_id}/generate",
        json={
            "title": "Bridge Deck Pavement Audit",
            "inspector_name": "Chief Highway Engineer",
            "location_notes": "Span 4 Eastbound",
            "additional_notes": "Immediate asphalt patch repair requested."
        }
    )
    assert gen_res.status_code == 200
    report_data = gen_res.json()
    assert report_data["detection_id"] == det_id
    assert report_data["file_size_bytes"] > 0
    assert report_data["download_url"] == f"/api/v1/reports/{det_id}/pdf"

    # 3. Test download PDF
    pdf_res = client.get(f"/api/v1/reports/{det_id}/pdf")
    assert pdf_res.status_code == 200
    assert pdf_res.headers["content-type"] == "application/pdf"
    assert len(pdf_res.content) > 1000  # Valid non-empty PDF binary

