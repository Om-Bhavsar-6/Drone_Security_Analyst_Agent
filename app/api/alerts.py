from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from app.storage.repositories import AlertRepository
from app.models.alert import SeverityLevel

router = APIRouter(tags=["Security Alerts"])
alert_repo = AlertRepository()

@router.get("/alerts")
def get_alerts(min_severity: Optional[SeverityLevel] = None):
    """Fetch all security notifications triggered by the rule engine."""
    sev_str = min_severity.value if min_severity else None
    alerts = alert_repo.get_all_alerts(min_severity=sev_str)
    return {
        "status": "success",
        "total_alerts": len(alerts),
        "alerts": alerts
    }

@router.get("/alerts/{alert_id}")
def get_alert_by_id(alert_id: str):
    """Fetch details for a specific security alert."""
    alert = alert_repo.get_alert(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail=f"Alert '{alert_id}' not found.")
    return {
        "status": "success",
        "data": alert
    }
