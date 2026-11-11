from datetime import datetime, timedelta
from typing import Dict, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.app.db.session import get_db
from backend.app.models.detection import DetectionRecord, DamageInstance
from backend.app.schemas.analytics import (
    AnalyticsOverviewResponse,
    SeverityBreakdown,
    DamageTypeCount,
    TimelineDataPoint
)

router = APIRouter()

CLASS_CODE_TO_NAME = {
    "D00": "Longitudinal Crack",
    "D10": "Transverse Crack",
    "D20": "Alligator Crack",
    "D40": "Pothole",
}


@router.get("/analytics/overview", response_model=AnalyticsOverviewResponse)
def get_analytics_overview(db: Session = Depends(get_db)):
    records = db.query(DetectionRecord).all()
    total_inspections = len(records)

    if total_inspections == 0:
        return AnalyticsOverviewResponse(
            total_inspections=0,
            total_damages_detected=0,
            average_severity_score=0.0,
            average_inference_time_ms=0.0,
            severity_breakdown=SeverityBreakdown(low=0, medium=0, high=0),
            damage_type_breakdown=[
                DamageTypeCount(class_code=code, class_name=name, count=0, percentage=0.0)
                for code, name in CLASS_CODE_TO_NAME.items()
            ],
            timeline=[]
        )

    # 1. Total damages & scores
    total_damages = sum(r.total_damages for r in records)
    avg_score = round(sum(r.severity_score for r in records) / total_inspections, 2)
    avg_inference = round(sum(r.inference_time_ms for r in records) / total_inspections, 2)

    # 2. Severity breakdown
    sev_counts = {"Low": 0, "Medium": 0, "High": 0}
    for r in records:
        sev = r.severity_level.capitalize()
        sev_counts[sev] = sev_counts.get(sev, 0) + 1

    severity_breakdown = SeverityBreakdown(
        low=sev_counts.get("Low", 0),
        medium=sev_counts.get("Medium", 0),
        high=sev_counts.get("High", 0)
    )

    # 3. Damage types breakdown from DamageInstance table
    dmg_instances = db.query(DamageInstance).all()
    total_inst = len(dmg_instances)
    type_counts = {"D00": 0, "D10": 0, "D20": 0, "D40": 0}

    for inst in dmg_instances:
        for code in type_counts.keys():
            if code in inst.class_name:
                type_counts[code] += 1
                break

    damage_type_breakdown = []
    for code, count in type_counts.items():
        pct = round((count / total_inst * 100.0), 1) if total_inst > 0 else 0.0
        damage_type_breakdown.append(
            DamageTypeCount(
                class_code=code,
                class_name=CLASS_CODE_TO_NAME.get(code, code),
                count=count,
                percentage=pct
            )
        )

    # 4. Recent timeline (last 7 days)
    today = datetime.utcnow().date()
    day_counts: Dict[str, Dict[str, int]] = {}
    for i in range(6, -1, -1):
        day_str = (today - timedelta(days=i)).strftime("%b %d")
        day_counts[day_str] = {"total": 0, "high": 0}

    for r in records:
        if r.created_at:
            r_day = r.created_at.strftime("%b %d")
            if r_day in day_counts:
                day_counts[r_day]["total"] += 1
                if r.severity_level.lower() == "high":
                    day_counts[r_day]["high"] += 1

    timeline = [
        TimelineDataPoint(
            date=day_str,
            inspections_count=stats["total"],
            high_severity_count=stats["high"]
        )
        for day_str, stats in day_counts.items()
    ]

    return AnalyticsOverviewResponse(
        total_inspections=total_inspections,
        total_damages_detected=total_damages,
        average_severity_score=avg_score,
        average_inference_time_ms=avg_inference,
        severity_breakdown=severity_breakdown,
        damage_type_breakdown=damage_type_breakdown,
        timeline=timeline
    )

