"""
Alert Agent – Monitors Critical patients and emits AlertEvents.
Called after each diagnosis to check if a new Critical alert should fire.
"""
from __future__ import annotations
from models.patient import Patient, AlertEvent, SeverityLevel
from store.memory_store import store


class AlertAgent:
    """
    Triggers alerts when:
      - A new Critical patient is registered
      - A patient's severity escalates to Critical
    """

    def check_and_alert(self, patient: Patient) -> AlertEvent | None:
        """
        Checks if the patient warrants a Critical alert.
        Returns the AlertEvent if one was created, else None.
        """
        if patient.severity != SeverityLevel.CRITICAL:
            return None

        if patient.is_alerted:
            return None  # Already alerted for this patient

        # Build alert message
        symptoms_short = patient.symptoms[:100] + ("..." if len(patient.symptoms) > 100 else "")
        message = (
            f"⚠️ CRITICAL ALERT: {patient.name} ({patient.age}y, {patient.gender}) "
            f"requires IMMEDIATE attention. Reason: {symptoms_short}"
        )

        alert = AlertEvent(
            patient_id=patient.patient_id,
            patient_name=patient.name,
            severity=patient.severity,
            message=message,
        )

        # Store the alert and mark the patient as alerted
        store.add_alert(alert)
        patient.is_alerted = True
        store.upsert_patient(patient)

        return alert

    def get_active_alerts(self) -> list:
        """Returns all unacknowledged alerts, newest first."""
        alerts = store.get_alerts(unacknowledged_only=False)
        return sorted(alerts, key=lambda a: a.triggered_at, reverse=True)

    def get_active_alerts_payload(self) -> list[dict]:
        alerts = self.get_active_alerts()
        return [
            {
                "alert_id": a.alert_id,
                "patient_id": a.patient_id,
                "patient_name": a.patient_name,
                "severity": a.severity,
                "message": a.message,
                "triggered_at": a.triggered_at.isoformat(),
                "acknowledged": a.acknowledged,
            }
            for a in alerts[:20]  # Cap at 20 for WebSocket payload
        ]


alert_agent = AlertAgent()
