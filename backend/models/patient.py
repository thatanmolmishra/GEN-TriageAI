from __future__ import annotations
import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum


class SeverityLevel(str, Enum):
    CRITICAL = "Critical"
    URGENT = "Urgent"
    MINOR = "Minor"


class PatientStatus(str, Enum):
    WAITING = "waiting"
    IN_TREATMENT = "in_treatment"
    TREATED = "treated"
    DISCHARGED = "discharged"


# ── Intake ──────────────────────────────────────────────────────────────────────
class PatientIntakeRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    age: int = Field(..., ge=0, le=150)
    gender: str = Field(default="Unknown")
    symptoms: str = Field(..., min_length=3, description="Chief complaint & symptoms")
    vitals: Optional[str] = Field(None, description="Vitals if available (e.g. BP, HR, SpO2)")
    notes: Optional[str] = None


# ── Diagnosis ───────────────────────────────────────────────────────────────────
class SeverityResult(BaseModel):
    severity: SeverityLevel
    confidence: float = Field(..., ge=0.0, le=1.0)
    reasoning: str
    recommended_actions: List[str]
    estimated_wait_minutes: int = Field(default=0)


# ── Patient (full record) ────────────────────────────────────────────────────────
class Patient(BaseModel):
    patient_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    age: int
    gender: str
    symptoms: str
    vitals: Optional[str] = None
    notes: Optional[str] = None
    severity: Optional[SeverityLevel] = None
    confidence: Optional[float] = None
    reasoning: Optional[str] = None
    recommended_actions: List[str] = Field(default_factory=list)
    estimated_wait_minutes: int = 0
    status: PatientStatus = PatientStatus.WAITING
    priority_score: float = 0.0
    arrived_at: datetime = Field(default_factory=datetime.utcnow)
    assessed_at: Optional[datetime] = None
    is_alerted: bool = False

    def to_queue_item(self) -> dict:
        """Compact representation for queue display."""
        return {
            "patient_id": self.patient_id,
            "name": self.name,
            "age": self.age,
            "gender": self.gender,
            "symptoms": self.symptoms[:80] + ("..." if len(self.symptoms) > 80 else ""),
            "severity": self.severity,
            "confidence": self.confidence,
            "status": self.status,
            "priority_score": self.priority_score,
            "arrived_at": self.arrived_at.isoformat(),
            "assessed_at": self.assessed_at.isoformat() if self.assessed_at else None,
            "is_alerted": self.is_alerted,
            "estimated_wait_minutes": self.estimated_wait_minutes,
        }


# ── Alert ────────────────────────────────────────────────────────────────────────
class AlertEvent(BaseModel):
    alert_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    patient_id: str
    patient_name: str
    severity: SeverityLevel
    message: str
    triggered_at: datetime = Field(default_factory=datetime.utcnow)
    acknowledged: bool = False


# ── API Responses ────────────────────────────────────────────────────────────────
class IntakeResponse(BaseModel):
    patient_id: str
    name: str
    severity: SeverityLevel
    confidence: float
    reasoning: str
    recommended_actions: List[str]
    estimated_wait_minutes: int
    message: str


class QueueResponse(BaseModel):
    total: int
    critical_count: int
    urgent_count: int
    minor_count: int
    patients: List[dict]


class StatusUpdateRequest(BaseModel):
    status: PatientStatus


class WebSocketPayload(BaseModel):
    type: str  # "queue_update" | "alert" | "heartbeat"
    timestamp: str
    data: dict
