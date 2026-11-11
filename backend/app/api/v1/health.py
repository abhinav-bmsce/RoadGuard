from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from backend.app.db.session import get_db
from backend.app.services.inference_engine import inference_engine

router = APIRouter()


@router.get("/health")
def check_health(db: Session = Depends(get_db)):
    db_status = "connected"
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    return {
        "status": "healthy",
        "service": "RoadGuard Backend API",
        "version": "1.0.0",
        "database": db_status,
        "deep_learning": {
            "model_loaded": inference_engine.is_loaded,
            "device": inference_engine.device_name,
            "architecture": "YOLOv8n (RDD2022)"
        }
    }

