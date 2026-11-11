import uuid
from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    Boolean,
    DateTime,
    ForeignKey,
    Text,
    JSON,
)
from sqlalchemy.orm import relationship
from backend.app.db.base import Base


class ModelVersion(Base):
    __tablename__ = "model_versions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    version = Column(String(50), nullable=False)
    architecture = Column(String(50), nullable=False)
    weights_path = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    detections = relationship("DetectionRecord", back_populates="model_version")


class ImageMetadata(Base):
    __tablename__ = "image_metadata"

    id = Column(Integer, primary_key=True, index=True)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size_bytes = Column(Integer, nullable=False)
    mime_type = Column(String(100), nullable=False)
    width = Column(Integer, nullable=False)
    height = Column(Integer, nullable=False)
    hash_md5 = Column(String(64), nullable=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    detections = relationship("DetectionRecord", back_populates="image", cascade="all, delete-orphan")


class DetectionRecord(Base):
    __tablename__ = "detection_records"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    image_id = Column(Integer, ForeignKey("image_metadata.id", ondelete="CASCADE"), nullable=False)
    model_version_id = Column(Integer, ForeignKey("model_versions.id"), nullable=True)
    annotated_image_path = Column(String(500), nullable=False)
    total_damages = Column(Integer, default=0)
    severity_level = Column(String(20), nullable=False)  # "Low", "Medium", "High"
    severity_score = Column(Float, nullable=False)       # 0 - 100 (RDSI)
    inference_time_ms = Column(Float, default=0.0)
    damage_summary = Column(JSON, default=dict)          # {"D00": 1, "D40": 2, ...}
    status = Column(String(20), default="completed")
    location_notes = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    image = relationship("ImageMetadata", back_populates="detections")
    model_version = relationship("ModelVersion", back_populates="detections")
    damages = relationship("DamageInstance", back_populates="detection", cascade="all, delete-orphan")
    reports = relationship("DetectionReport", back_populates="detection", cascade="all, delete-orphan")


class DamageInstance(Base):
    __tablename__ = "damage_instances"

    id = Column(Integer, primary_key=True, index=True)
    detection_id = Column(String(36), ForeignKey("detection_records.id", ondelete="CASCADE"), nullable=False)
    class_id = Column(Integer, nullable=False)
    class_name = Column(String(50), nullable=False)
    confidence = Column(Float, nullable=False)
    bbox_xmin = Column(Float, nullable=False)
    bbox_ymin = Column(Float, nullable=False)
    bbox_xmax = Column(Float, nullable=False)
    bbox_ymax = Column(Float, nullable=False)
    area_ratio = Column(Float, nullable=False)           # area / total image area
    instance_severity = Column(Float, nullable=False)     # instance score
    severity_tag = Column(String(20), nullable=False)     # Low, Medium, High

    detection = relationship("DetectionRecord", back_populates="damages")


class DetectionReport(Base):
    __tablename__ = "detection_reports"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    detection_id = Column(String(36), ForeignKey("detection_records.id", ondelete="CASCADE"), nullable=False)
    report_title = Column(String(255), nullable=False)
    pdf_path = Column(String(500), nullable=False)
    file_size_bytes = Column(Integer, default=0)
    summary_notes = Column(Text, nullable=True)
    generated_at = Column(DateTime, default=datetime.utcnow)

    detection = relationship("DetectionRecord", back_populates="reports")

