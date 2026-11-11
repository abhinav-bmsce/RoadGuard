import os
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.db.session import get_db
from backend.app.models.detection import DetectionRecord, DetectionReport
from backend.app.schemas.report import ReportGenerateRequest, ReportResponse
from backend.app.services.report_generator import ReportGenerator

router = APIRouter()


@router.post("/reports/{detection_id}/generate", response_model=ReportResponse)
def generate_report(
    detection_id: str,
    payload: ReportGenerateRequest,
    db: Session = Depends(get_db)
):
    record = db.query(DetectionRecord).filter(DetectionRecord.id == detection_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Detection record not found")

    # Serialize detection data for report generator
    detection_dict = {
        "original_filename": record.image.original_filename if record.image else "pavement_scan.jpg",
        "annotated_image_path": record.annotated_image_path,
        "total_damages": record.total_damages,
        "severity_level": record.severity_level,
        "severity_score": record.severity_score,
        "inference_time_ms": record.inference_time_ms,
        "damages": [
            {
                "class_name": d.class_name,
                "confidence": d.confidence,
                "area_ratio": d.area_ratio,
                "instance_severity": d.instance_severity,
                "severity_tag": d.severity_tag,
            }
            for d in record.damages
        ]
    }

    pdf_path = ReportGenerator.generate_pdf(
        report_id=record.id,
        detection_data=detection_dict,
        inspector_name=payload.inspector_name or "Civil Infrastructure Inspector",
        location_notes=payload.location_notes or record.location_notes or "Unspecified Road Link"
    )

    file_size = os.path.getsize(pdf_path) if os.path.exists(pdf_path) else 0

    report_record = DetectionReport(
        detection_id=record.id,
        report_title=payload.title,
        pdf_path=pdf_path,
        file_size_bytes=file_size,
        summary_notes=payload.additional_notes
    )
    db.add(report_record)
    db.commit()
    db.refresh(report_record)

    return ReportResponse(
        id=report_record.id,
        detection_id=record.id,
        report_title=report_record.report_title,
        download_url=f"/api/v1/reports/{record.id}/pdf",
        file_size_bytes=file_size,
        generated_at=report_record.generated_at
    )


@router.get("/reports/{detection_id}/pdf")
def download_pdf_report(detection_id: str, db: Session = Depends(get_db)):
    record = db.query(DetectionRecord).filter(DetectionRecord.id == detection_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Detection record not found")

    pdf_filename = f"RoadGuard_Report_{record.id}.pdf"
    pdf_path = os.path.join(settings.UPLOAD_DIR, "reports", pdf_filename)

    # If PDF has not been generated yet, generate it on-the-fly
    if not os.path.exists(pdf_path):
        detection_dict = {
            "original_filename": record.image.original_filename if record.image else "pavement_scan.jpg",
            "annotated_image_path": record.annotated_image_path,
            "total_damages": record.total_damages,
            "severity_level": record.severity_level,
            "severity_score": record.severity_score,
            "inference_time_ms": record.inference_time_ms,
            "damages": [
                {
                    "class_name": d.class_name,
                    "confidence": d.confidence,
                    "area_ratio": d.area_ratio,
                    "instance_severity": d.instance_severity,
                    "severity_tag": d.severity_tag,
                }
                for d in record.damages
            ]
        }
        pdf_path = ReportGenerator.generate_pdf(
            report_id=record.id,
            detection_data=detection_dict,
            inspector_name="Civil Infrastructure Inspector",
            location_notes=record.location_notes or "Highway Inspection Link"
        )

    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename=pdf_filename
    )

