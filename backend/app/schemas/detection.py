from typing import List, Dict, Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class BoundingBox(BaseModel):
    xmin: float = Field(..., description="Top-left X coordinate in pixels")
    ymin: float = Field(..., description="Top-left Y coordinate in pixels")
    xmax: float = Field(..., description="Bottom-right X coordinate in pixels")
    ymax: float = Field(..., description="Bottom-right Y coordinate in pixels")


class DamageInstanceItem(BaseModel):
    id: Optional[int] = None
    class_id: int
    class_name: str
    confidence: float
    bbox: BoundingBox
    area_ratio: float
    instance_severity: float
    severity_tag: str

    model_config = ConfigDict(from_attributes=True)


class DetectionResultResponse(BaseModel):
    id: str
    created_at: datetime
    original_filename: str
    image_width: int
    image_height: int
    original_image_url: str
    annotated_image_url: str
    total_damages: int
    severity_level: str  # "Low", "Medium", "High"
    severity_score: float  # 0 to 100 (RDSI)
    inference_time_ms: float
    damage_summary: Dict[str, int]
    damages: List[DamageInstanceItem]
    severity_disclaimer: str = (
        "EXPERIMENTAL ESTIMATE (Non-Certified): Severity ratings (Low/Medium/High) are heuristic "
        "AI screening metrics. They do not replace certified ASTM D6433 structural engineering pavement ratings."
    )
    location_notes: Optional[str] = None
    status: str = "completed"

    model_config = ConfigDict(from_attributes=True)
