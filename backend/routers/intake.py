"""
POST /api/intake – Accept patient symptoms, run agents, return severity assessment.
"""
from fastapi import APIRouter, HTTPException
from datetime import datetime

from models.patient import (
    PatientIntakeRequest,
    IntakeResponse,
    Patient,
    SeverityLevel,
)
from agents.intake_agent import intake_agent
from agents.diagnosis_agent import diagnosis_agent
from agents.alert_agent import alert_agent
from agents.dashboard_agent import dashboard_agent
from store.memory_store import store

router = APIRouter(prefix="/api", tags=["Intake"])


@router.post("/intake", response_model=IntakeResponse)
async def submit_intake(request: PatientIntakeRequest):
    """
    Patient symptom intake endpoint.
    Runs: IntakeAgent → DiagnosisAgent → PriorityQueueAgent → AlertAgent
    Returns the severity assessment immediately.
    """
    # Step 1: Intake Agent – validate & normalise
    intake_result = intake_agent.run(request)
    if not intake_result["valid"]:
        raise HTTPException(status_code=422, detail=intake_result["errors"])

    cleaned = intake_result["patient"]

    # Step 2: Diagnosis Agent – call Gemini
    severity_result = await diagnosis_agent.run(
        name=cleaned["name"],
        age=cleaned["age"],
        gender=cleaned["gender"],
        symptoms=cleaned["symptoms"],
        vitals=cleaned.get("vitals"),
        notes=cleaned.get("notes"),
    )

    # Step 3: Build Patient record and persist
    patient = Patient(
        name=cleaned["name"],
        age=cleaned["age"],
        gender=cleaned["gender"],
        symptoms=cleaned["symptoms"],
        vitals=cleaned.get("vitals"),
        notes=cleaned.get("notes"),
        severity=severity_result.severity,
        confidence=severity_result.confidence,
        reasoning=severity_result.reasoning,
        recommended_actions=severity_result.recommended_actions,
        estimated_wait_minutes=severity_result.estimated_wait_minutes,
        assessed_at=datetime.utcnow(),
    )
    store.upsert_patient(patient)

    # Step 4: Alert Agent – trigger if Critical
    new_alert = alert_agent.check_and_alert(patient)

    # Step 5: Dashboard Agent – push immediate WebSocket update
    queue_payload = dashboard_agent.build_queue_payload()
    await dashboard_agent.push_immediate(queue_payload)

    if new_alert:
        alert_payload = dashboard_agent.build_alert_payload(alert=new_alert)
        await dashboard_agent.push_immediate(alert_payload)

    severity_labels = {
        SeverityLevel.CRITICAL: "🔴 CRITICAL – Immediate treatment required",
        SeverityLevel.URGENT:   "🟠 URGENT – Please wait, you will be seen shortly",
        SeverityLevel.MINOR:    "🟢 MINOR – Please wait in the waiting area",
    }

    return IntakeResponse(
        patient_id=patient.patient_id,
        name=patient.name,
        severity=severity_result.severity,
        confidence=severity_result.confidence,
        reasoning=severity_result.reasoning,
        recommended_actions=severity_result.recommended_actions,
        estimated_wait_minutes=severity_result.estimated_wait_minutes,
        message=severity_labels[severity_result.severity],
    )
