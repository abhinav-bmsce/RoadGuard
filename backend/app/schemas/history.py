from typing import List, Dict, Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class HistoryItemResponse(BaseModel):
    id: str
    created_at: datetime
    original_filename: str
    original_image_url: str
    annotated_image_url: str
    total_damages: int
    severity_level: str
    severity_score: float
    inference_time_ms: float
    damage_summary: Dict[str, int]
    location_notes: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class HistoryListResponse(BaseModel):
    items: List[HistoryItemResponse]
    total: int
    page: int
    limit: int
    total_pages: int
