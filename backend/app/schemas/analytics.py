from typing import Dict, List
from pydantic import BaseModel


class SeverityBreakdown(BaseModel):
    low: int
    medium: int
    high: int


class DamageTypeCount(BaseModel):
    class_code: str
    class_name: str
    count: int
    percentage: float


class TimelineDataPoint(BaseModel):
    date: str
    inspections_count: int
    high_severity_count: int


class AnalyticsOverviewResponse(BaseModel):
    total_inspections: int
    total_damages_detected: int
    average_severity_score: float
    average_inference_time_ms: float
    severity_breakdown: SeverityBreakdown
    damage_type_breakdown: List[DamageTypeCount]
    timeline: List[TimelineDataPoint]

