"""
RoadGuard - Database Seeder
Populates PostgreSQL / SQLite database with realistic historical road inspection surveys across multiple days.
Enables instant, rich visualization of dashboard analytics, charts, and history logs out of the box.
"""

import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from sqlalchemy.orm import Session

from backend.app.db.session import SessionLocal, engine
from backend.app.db.base import Base
from backend.app.models.detection import (
    ImageMetadata,
    DetectionRecord,
    DamageInstance,
    ModelVersion,
)
from backend.app.services.visualizer import Visualizer

# Realistic road survey links
SAMPLE_LOCATIONS = [
    "Interstate 80 Eastbound (Mile 14.2)",
    "State Route 101 Northbound (Exit 42)",
    "Pacific Coast Highway (Section 3)",
    "Municipal Boulevard & 5th Ave",
    "County Road 12 (Bridge Approach)",
    "Airport Access Road (Westbound)",
    "Harbor Expressway (Pier 9)",
    "North Loop Freeway (Chainage 18+400)",
    "Southbound Industrial Parkway",
    "Downtown Commercial Corridor",
    "Outer Beltway (Milepost 88)",
    "Mountain Pass Highway (Curve 12)",
]

MOCK_INSPECTIONS = [
    {
        "filename": "road_pothole_severe.jpg",
        "days_ago": 0,
        "location": SAMPLE_LOCATIONS[0],
        "damages": [
            {"cls": 3, "name": "D40_Pothole", "conf": 0.89, "box": (238, 283, 402, 432), "area": 0.098, "score": 82.5, "tag": "High"}
        ],
        "overall_score": 82.5,
        "overall_sev": "High",
        "latency": 32.4
    },
    {
        "filename": "road_longitudinal_crack.jpg",
        "days_ago": 1,
        "location": SAMPLE_LOCATIONS[1],
        "damages": [
            {"cls": 0, "name": "D00_Longitudinal_Crack", "conf": 0.84, "box": (280, 50, 288, 570), "area": 0.010, "score": 9.2, "tag": "Low"}
        ],
        "overall_score": 9.2,
        "overall_sev": "Low",
        "latency": 31.8
    },
    {
        "filename": "road_transverse_crack.jpg",
        "days_ago": 1,
        "location": SAMPLE_LOCATIONS[2],
        "damages": [
            {"cls": 1, "name": "D10_Transverse_Crack", "conf": 0.81, "box": (60, 310, 560, 318), "area": 0.012, "score": 12.8, "tag": "Low"}
        ],
        "overall_score": 12.8,
        "overall_sev": "Low",
        "latency": 33.1
    },
    {
        "filename": "road_multi_hazard.jpg",
        "days_ago": 2,
        "location": SAMPLE_LOCATIONS[3],
        "damages": [
            {"cls": 2, "name": "D20_Alligator_Crack", "conf": 0.86, "box": (120, 200, 320, 380), "area": 0.088, "score": 62.4, "tag": "High"},
            {"cls": 3, "name": "D40_Pothole", "conf": 0.91, "box": (450, 420, 550, 520), "area": 0.024, "score": 44.8, "tag": "Medium"}
        ],
        "overall_score": 68.2,
        "overall_sev": "High",
        "latency": 36.5
    },
    {
        "filename": "road_pothole_severe.jpg",
        "days_ago": 3,
        "location": SAMPLE_LOCATIONS[4],
        "damages": [
            {"cls": 3, "name": "D40_Pothole", "conf": 0.76, "box": (210, 260, 350, 390), "area": 0.044, "score": 58.2, "tag": "Medium"}
        ],
        "overall_score": 58.2,
        "overall_sev": "Medium",
        "latency": 30.9
    },
    {
        "filename": "road_longitudinal_crack.jpg",
        "days_ago": 4,
        "location": SAMPLE_LOCATIONS[5],
        "damages": [
            {"cls": 0, "name": "D00_Longitudinal_Crack", "conf": 0.79, "box": (250, 80, 258, 480), "area": 0.008, "score": 7.8, "tag": "Low"},
            {"cls": 0, "name": "D00_Longitudinal_Crack", "conf": 0.72, "box": (380, 120, 386, 390), "area": 0.005, "score": 5.4, "tag": "Low"}
        ],
        "overall_score": 11.2,
        "overall_sev": "Low",
        "latency": 34.0
    },
    {
        "filename": "road_transverse_crack.jpg",
        "days_ago": 4,
        "location": SAMPLE_LOCATIONS[6],
        "damages": [
            {"cls": 1, "name": "D10_Transverse_Crack", "conf": 0.88, "box": (90, 280, 510, 290), "area": 0.011, "score": 12.1, "tag": "Low"}
        ],
        "overall_score": 12.1,
        "overall_sev": "Low",
        "latency": 32.7
    },
    {
        "filename": "road_multi_hazard.jpg",
        "days_ago": 5,
        "location": SAMPLE_LOCATIONS[7],
        "damages": [
            {"cls": 2, "name": "D20_Alligator_Crack", "conf": 0.82, "box": (140, 180, 310, 340), "area": 0.066, "score": 53.6, "tag": "Medium"},
            {"cls": 0, "name": "D00_Longitudinal_Crack", "conf": 0.75, "box": (480, 100, 488, 450), "area": 0.007, "score": 6.9, "tag": "Low"}
        ],
        "overall_score": 48.5,
        "overall_sev": "Medium",
        "latency": 35.2
    },
    {
        "filename": "road_pothole_severe.jpg",
        "days_ago": 6,
        "location": SAMPLE_LOCATIONS[8],
        "damages": [
            {"cls": 3, "name": "D40_Pothole", "conf": 0.94, "box": (220, 290, 410, 440), "area": 0.102, "score": 85.0, "tag": "High"}
        ],
        "overall_score": 85.0,
        "overall_sev": "High",
        "latency": 33.8
    }
]


def seed_database():
    print("=" * 60)
    print(" RoadGuard - Seeding Demonstration Pavement Audits")
    print("=" * 60)

    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()

    try:
        # Check if ModelVersion exists
        mv = db.query(ModelVersion).first()
        if not mv:
            mv = ModelVersion(
                name="RoadGuard YOLOv8n RDD2022",
                version="1.0.0",
                architecture="YOLOv8n-AnchorFree",
                weights_path="ml/models/roadguard_yolov8n.pt",
                is_active=True
            )
            db.add(mv)
            db.commit()
            db.refresh(mv)

        sample_src_dir = Path("ml/inference/samples")
        upload_img_dir = Path("backend/uploads/images")
        upload_ann_dir = Path("backend/uploads/annotated")
        upload_img_dir.mkdir(parents=True, exist_ok=True)
        upload_ann_dir.mkdir(parents=True, exist_ok=True)

        now = datetime.now(timezone.utc)
        count = 0

        for mock in MOCK_INSPECTIONS:
            rec_id = str(uuid.uuid4())
            src_file = sample_src_dir / mock["filename"]
            if not src_file.exists():
                continue

            target_orig = upload_img_dir / f"{rec_id}.jpg"
            target_ann = upload_ann_dir / f"annotated_{rec_id}.jpg"

            # Copy sample file
            with open(src_file, "rb") as fsrc, open(target_orig, "wb") as fdst:
                fdst.write(fsrc.read())

            # Prepare damage list format for visualizer
            viz_damages = []
            damage_summary = {}
            for d in mock["damages"]:
                box = d["box"]
                viz_damages.append({
                    "class_id": d["cls"],
                    "class_name": d["name"],
                    "confidence": d["conf"],
                    "bbox": {"xmin": box[0], "ymin": box[1], "xmax": box[2], "ymax": box[3]},
                    "area_ratio": d["area"],
                    "instance_severity": d["score"],
                    "severity_tag": d["tag"]
                })
                short_code = d["name"].split("_")[0]
                damage_summary[short_code] = damage_summary.get(short_code, 0) + 1

            # Generate annotated image
            Visualizer.annotate_image(
                image_path=str(target_orig),
                damages=viz_damages,
                output_path=str(target_ann),
                overall_severity=mock["overall_sev"],
                overall_score=mock["overall_score"]
            )

            created_timestamp = now - timedelta(days=mock["days_ago"], hours=mock["days_ago"] * 2)

            img_meta = ImageMetadata(
                original_filename=mock["filename"],
                file_path=str(target_orig),
                file_size_bytes=target_orig.stat().st_size,
                mime_type="image/jpeg",
                width=640,
                height=640,
                uploaded_at=created_timestamp
            )
            db.add(img_meta)
            db.flush()

            rec = DetectionRecord(
                id=rec_id,
                image_id=img_meta.id,
                model_version_id=mv.id,
                annotated_image_path=str(target_ann),
                total_damages=len(mock["damages"]),
                severity_level=mock["overall_sev"],
                severity_score=mock["overall_score"],
                inference_time_ms=mock["latency"],
                damage_summary=damage_summary,
                location_notes=mock["location"],
                status="completed",
                created_at=created_timestamp
            )
            db.add(rec)
            db.flush()

            for d in viz_damages:
                inst = DamageInstance(
                    detection_id=rec.id,
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

            count += 1

        db.commit()
        print(f"Successfully seeded {count} road inspection audit records into database!")

    except Exception as e:
        db.rollback()
        print(f"Seeding failed: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()

