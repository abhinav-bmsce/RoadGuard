import os
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.app.db.session import get_db
from backend.app.models.detection import DetectionRecord
from backend.app.schemas.history import HistoryListResponse, HistoryItemResponse

router = APIRouter()


@router.get("/history", response_model=HistoryListResponse)
def get_history(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    severity: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(DetectionRecord)

    if severity and severity.lower() != "all":
        query = query.filter(DetectionRecord.severity_level.ilike(severity))

    if search:
        query = query.filter(DetectionRecord.location_notes.ilike(f"%{search}%"))

    total = query.count()
    total_pages = max(1, (total + limit - 1) // limit)
    offset = (page - 1) * limit

    records = query.order_by(desc(DetectionRecord.created_at)).offset(offset).limit(limit).all()

    items = []
    for r in records:
        orig_filename = r.image.original_filename if r.image else "image.jpg"
        orig_img_name = Path(r.image.file_path).name if r.image else ""
        annotated_img_name = Path(r.annotated_image_path).name if r.annotated_image_path else ""

        items.append(
            HistoryItemResponse(
                id=r.id,
                created_at=r.created_at,
                original_filename=orig_filename,
                original_image_url=f"/uploads/images/{orig_img_name}",
                annotated_image_url=f"/uploads/annotated/{annotated_img_name}",
                total_damages=r.total_damages,
                severity_level=r.severity_level,
                severity_score=r.severity_score,
                inference_time_ms=r.inference_time_ms,
                damage_summary=r.damage_summary or {},
                location_notes=r.location_notes
            )
        )

    return HistoryListResponse(
        items=items,
        total=total,
        page=page,
        limit=limit,
        total_pages=total_pages
    )


@router.delete("/history/{detection_id}")
def delete_detection(detection_id: str, db: Session = Depends(get_db)):
    record = db.query(DetectionRecord).filter(DetectionRecord.id == detection_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Detection record not found")

    # Clean up files on disk if they exist
    if record.annotated_image_path and os.path.exists(record.annotated_image_path):
        try:
            os.remove(record.annotated_image_path)
        except Exception:
            pass

    if record.image and record.image.file_path and os.path.exists(record.image.file_path):
        try:
            os.remove(record.image.file_path)
        except Exception:
            pass

    db.delete(record)
    db.commit()
    return {"message": f"Detection {detection_id} deleted successfully"}

