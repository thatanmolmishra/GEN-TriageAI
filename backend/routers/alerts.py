"""
GET /api/alerts – Returns active alerts.
PATCH /api/alerts/{alert_id}/acknowledge – Acknowledges an alert.
"""
from fastapi import APIRouter, HTTPException
from agents.alert_agent import alert_agent
from store.memory_store import store

router = APIRouter(prefix="/api", tags=["Alerts"])


@router.get("/alerts")
def get_alerts(unacknowledged_only: bool = False):
    """Return all alerts (newest first). Optionally filter to unacknowledged."""
    alerts = store.get_alerts(unacknowledged_only=unacknowledged_only)
    return {
        "total": len(alerts),
        "alerts": [
            {
                "alert_id": a.alert_id,
                "patient_id": a.patient_id,
                "patient_name": a.patient_name,
                "severity": a.severity,
                "message": a.message,
                "triggered_at": a.triggered_at.isoformat(),
                "acknowledged": a.acknowledged,
            }
            for a in sorted(alerts, key=lambda x: x.triggered_at, reverse=True)
        ],
    }


@router.patch("/alerts/{alert_id}/acknowledge")
def acknowledge_alert(alert_id: str):
    """Mark a specific alert as acknowledged."""
    success = store.acknowledge_alert(alert_id)
    if not success:
        raise HTTPException(status_code=404, detail="Alert not found")
    return {"message": "Alert acknowledged", "alert_id": alert_id}
