from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class ReportGenerateRequest(BaseModel):
    title: Optional[str] = "RoadGuard Structural Distress Inspection Report"
    inspector_name: Optional[str] = "Civil Infrastructure Inspector"
    location_notes: Optional[str] = None
    additional_notes: Optional[str] = None


class ReportResponse(BaseModel):
    id: str
    detection_id: str
    report_title: str
    download_url: str
    file_size_bytes: int
    generated_at: datetime

