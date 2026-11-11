import os
import uuid
import hashlib
import shutil
from pathlib import Path
from typing import Optional, List
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.db.session import get_db
from backend.app.models.detection import DetectionRecord, DamageInstance, ImageMetadata, ModelVersion
from backend.app.schemas.detection import DetectionResultResponse, DamageInstanceItem, BoundingBox
from backend.app.services.inference_engine import inference_engine
from backend.app.services.severity_analyzer import SeverityAnalyzer
from backend.app.services.visualizer import Visualizer

router = APIRouter()


@router.post("/detect", response_model=DetectionResultResponse)
async def detect_road_damage(
    file: UploadFile = File(...),
    confidence: Optional[float] = Form(None),
    location_notes: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    # 1. Validate file extension
    ext = file.filename.split(".")[-1].lower() if "." in file.filename else ""
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format '{ext}'. Allowed: {settings.ALLOWED_EXTENSIONS}"
        )

    # 2. Read and validate file content
    contents = await file.read()
    file_size = len(contents)
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if file_size > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE_MB}MB."
        )

    # 3. Generate unique filenames and save original file
    file_id = str(uuid.uuid4())
    img_filename = f"{file_id}.{ext}"
    orig_save_dir = Path(settings.UPLOAD_DIR) / "images"
    orig_save_dir.mkdir(parents=True, exist_ok=True)
    orig_save_path = orig_save_dir / img_filename

    with open(orig_save_path, "wb") as f:
        f.write(contents)

    # 4. Run real deep learning model inference
    try:
        raw_damages, inference_ms, img_w, img_h = inference_engine.detect(
            image_path=str(orig_save_path),
            conf_threshold=confidence
        )
    except Exception as e:
        logger.error(f"Inference failed on {file.filename}: {e}")
        if orig_save_path.exists():
            orig_save_path.unlink()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Inference failed: {str(e)}"
        )

    # 5. Severity Assessment Engine
    damage_instances_data = []
    damage_summary = {}

    for dmg in raw_damages:
        bbox = dmg["bbox"]
        c_name = dmg["class_name"]
        conf = dmg["confidence"]
        
        area_ratio, inst_score, tag = SeverityAnalyzer.calculate_instance_severity(
            bbox=bbox,
            confidence=conf,
            class_name=c_name,
            image_width=img_w,
            image_height=img_h
        )

        dmg_item = {
            "class_id": dmg["class_id"],
            "class_name": c_name,
            "confidence": conf,
            "bbox": bbox,
            "area_ratio": area_ratio,
            "instance_severity": inst_score,
            "severity_tag": tag
        }
        damage_instances_data.append(dmg_item)

        # Update category counts
        short_cls = c_name.split("_")[0]
        damage_summary[short_cls] = damage_summary.get(short_cls, 0) + 1

    cumulative_rdsi, overall_severity = SeverityAnalyzer.calculate_frame_severity(damage_instances_data)

    # 6. Render annotated visualization
    annotated_filename = f"annotated_{file_id}.jpg"
    annotated_save_path = Path(settings.UPLOAD_DIR) / "annotated" / annotated_filename
    Visualizer.annotate_image(
        image_path=str(orig_save_path),
        damages=damage_instances_data,
        output_path=str(annotated_save_path),
        overall_severity=overall_severity,
        overall_score=cumulative_rdsi
    )

    # 7. Persist to Database
    md5_hash = hashlib.md5(contents).hexdigest()
    image_meta = ImageMetadata(
        original_filename=file.filename,
        file_path=str(orig_save_path),
        file_size_bytes=file_size,
        mime_type=file.content_type or f"image/{ext}",
        width=img_w,
        height=img_h,
        hash_md5=md5_hash
    )
    db.add(image_meta)
    db.flush()

    detection_record = DetectionRecord(
        id=file_id,
        image_id=image_meta.id,
        annotated_image_path=str(annotated_save_path),
        total_damages=len(damage_instances_data),
        severity_level=overall_severity,
        severity_score=cumulative_rdsi,
        inference_time_ms=inference_ms,
        damage_summary=damage_summary,
        location_notes=location_notes,
        status="completed"
    )
    db.add(detection_record)
    db.flush()

    # Add damage instances
    for d in damage_instances_data:
        inst = DamageInstance(
            detection_id=detection_record.id,
            class_id=d["class_id"],
            class_name=d["class_name"],
            confidence=d["confidence"],
            bbox_xmin=d["bbox"]["xmin"],
            bbox_ymin=d["bbox"]["ymin"],
            bbox_xmax=d["bbox"]["xmax"],
            bbox_ymax=d["bbox"]["ymax"],
            area_ratio=d["area_ratio"],
            instance_severity=d["instance_severity"],
            severity_tag=d["severity_tag"]
        )
        db.add(inst)

    db.commit()
    db.refresh(detection_record)

    # 8. Construct Response
    return DetectionResultResponse(
        id=detection_record.id,
        created_at=detection_record.created_at,
        original_filename=image_meta.original_filename,
        image_width=image_meta.width,
        image_height=image_meta.height,
        original_image_url=f"/uploads/images/{img_filename}",
        annotated_image_url=f"/uploads/annotated/{annotated_filename}",
        total_damages=detection_record.total_damages,
        severity_level=detection_record.severity_level,
        severity_score=detection_record.severity_score,
        inference_time_ms=detection_record.inference_time_ms,
        damage_summary=detection_record.damage_summary,
        damages=[
            DamageInstanceItem(
                id=d.id,
                class_id=d.class_id,
                class_name=d.class_name,
                confidence=d.confidence,
                bbox=BoundingBox(
                    xmin=d.bbox_xmin,
                    ymin=d.bbox_ymin,
                    xmax=d.bbox_xmax,
                    ymax=d.bbox_ymax
                ),
                area_ratio=d.area_ratio,
                instance_severity=d.instance_severity,
                severity_tag=d.severity_tag
            )
            for d in detection_record.damages
        ],
        location_notes=detection_record.location_notes,
        status=detection_record.status
    )


@router.get("/detect/{detection_id}", response_model=DetectionResultResponse)
def get_detection(detection_id: str, db: Session = Depends(get_db)):
    record = db.query(DetectionRecord).filter(DetectionRecord.id == detection_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Detection record not found")

    orig_name = Path(record.image.file_path).name
    annotated_name = Path(record.annotated_image_path).name

    return DetectionResultResponse(
        id=record.id,
        created_at=record.created_at,
        original_filename=record.image.original_filename,
        image_width=record.image.width,
        image_height=record.image.height,
        original_image_url=f"/uploads/images/{orig_name}",
        annotated_image_url=f"/uploads/annotated/{annotated_name}",
        total_damages=record.total_damages,
        severity_level=record.severity_level,
        severity_score=record.severity_score,
        inference_time_ms=record.inference_time_ms,
        damage_summary=record.damage_summary,
        damages=[
            DamageInstanceItem(
                id=d.id,
                class_id=d.class_id,
                class_name=d.class_name,
                confidence=d.confidence,
                bbox=BoundingBox(
                    xmin=d.bbox_xmin,
                    ymin=d.bbox_ymin,
                    xmax=d.bbox_xmax,
                    ymax=d.bbox_ymax
                ),
                area_ratio=d.area_ratio,
                instance_severity=d.instance_severity,
                severity_tag=d.severity_tag
            )
            for d in record.damages
        ],
        location_notes=record.location_notes,
        status=record.status
    )

