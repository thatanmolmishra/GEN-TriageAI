"""
GET  /api/patients/{id}       – Full patient detail.
PATCH /api/patients/{id}/status – Update patient status.
DELETE /api/patients/{id}     – Remove patient from queue.
"""
from fastapi import APIRouter, HTTPException
from models.patient import StatusUpdateRequest
from store.memory_store import store
from agents.dashboard_agent import dashboard_agent
import asyncio

router = APIRouter(prefix="/api", tags=["Patients"])


@router.get("/patients/{patient_id}")
def get_patient(patient_id: str):
    """Get full patient record by ID."""
    patient = store.get_patient(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient.model_dump()


@router.patch("/patients/{patient_id}/status")
async def update_patient_status(patient_id: str, body: StatusUpdateRequest):
    """Update a patient's status (e.g. waiting → in_treatment → treated)."""
    patient = store.update_patient_status(patient_id, body.status)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Push WebSocket update
    payload = dashboard_agent.build_queue_payload()
    await dashboard_agent.push_immediate(payload)

    return {
        "message": f"Patient status updated to {body.status}",
        "patient_id": patient_id,
        "status": body.status,
    }


@router.delete("/patients/{patient_id}")
async def remove_patient(patient_id: str):
    """Remove a patient from the active queue."""
    success = store.delete_patient(patient_id)
    if not success:
        raise HTTPException(status_code=404, detail="Patient not found")

    payload = dashboard_agent.build_queue_payload()
    await dashboard_agent.push_immediate(payload)

    return {"message": "Patient removed from queue", "patient_id": patient_id}
