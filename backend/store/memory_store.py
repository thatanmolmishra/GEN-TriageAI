"""
Thread-safe in-memory store backed by SQLite for persistence.
Serves as the single source of truth for all agents.
"""
import sqlite3
import json
import asyncio
from datetime import datetime
from threading import Lock
from typing import Dict, List, Optional

from models.patient import Patient, AlertEvent, SeverityLevel, PatientStatus
from config import SEVERITY_BASE_SCORES, MINOR_ESCALATION_SECONDS, URGENT_ESCALATION_SECONDS

DB_PATH = "triageai.db"


class MemoryStore:
    def __init__(self):
        self._patients: Dict[str, Patient] = {}
        self._alerts: List[AlertEvent] = []
        self._lock = Lock()
        self._init_db()

    # ── SQLite Init ──────────────────────────────────────────────────────────────
    def _init_db(self):
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS patients (
                    patient_id TEXT PRIMARY KEY,
                    data       TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS alerts (
                    alert_id    TEXT PRIMARY KEY,
                    data        TEXT NOT NULL,
                    triggered_at TEXT NOT NULL
                )
            """)
            conn.commit()

    def _persist_patient(self, patient: Patient):
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO patients VALUES (?, ?, ?)",
                (patient.patient_id, patient.model_dump_json(), datetime.utcnow().isoformat()),
            )
            conn.commit()

    def _persist_alert(self, alert: AlertEvent):
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO alerts VALUES (?, ?, ?)",
                (alert.alert_id, alert.model_dump_json(), alert.triggered_at.isoformat()),
            )
            conn.commit()

    # ── Priority Scoring ─────────────────────────────────────────────────────────
    def _compute_priority_score(self, patient: Patient) -> float:
        """Higher score = higher priority in queue."""
        severity = patient.severity or SeverityLevel.MINOR
        base = SEVERITY_BASE_SCORES.get(severity.value, 1000)

        wait_seconds = (datetime.utcnow() - patient.arrived_at).total_seconds()

        # Escalation bonus: long-waiting patients get a boost
        if severity == SeverityLevel.MINOR and wait_seconds > MINOR_ESCALATION_SECONDS:
            base = SEVERITY_BASE_SCORES["Urgent"]
        elif severity == SeverityLevel.URGENT and wait_seconds > URGENT_ESCALATION_SECONDS:
            base = SEVERITY_BASE_SCORES["Critical"]

        # Add wait time component (0.1 point per second waited)
        score = base + (wait_seconds * 0.1)

        # Apply confidence multiplier
        confidence = patient.confidence or 0.7
        score *= (0.8 + confidence * 0.2)  # 80–100% of base depending on confidence

        return round(score, 2)

    # ── Patient CRUD ─────────────────────────────────────────────────────────────
    def upsert_patient(self, patient: Patient) -> Patient:
        with self._lock:
            patient.priority_score = self._compute_priority_score(patient)
            self._patients[patient.patient_id] = patient
            self._persist_patient(patient)
            return patient

    def get_patient(self, patient_id: str) -> Optional[Patient]:
        with self._lock:
            return self._patients.get(patient_id)

    def get_all_patients(self) -> List[Patient]:
        with self._lock:
            return list(self._patients.values())

    def get_active_patients(self) -> List[Patient]:
        """Patients not yet discharged."""
        with self._lock:
            return [
                p for p in self._patients.values()
                if p.status not in (PatientStatus.DISCHARGED,)
            ]

    def get_priority_queue(self) -> List[Patient]:
        """Active patients sorted by priority score (highest first)."""
        active = self.get_active_patients()
        # Recompute scores before sorting
        for p in active:
            p.priority_score = self._compute_priority_score(p)
        return sorted(active, key=lambda p: p.priority_score, reverse=True)

    def update_patient_status(self, patient_id: str, status: PatientStatus) -> Optional[Patient]:
        with self._lock:
            patient = self._patients.get(patient_id)
            if not patient:
                return None
            patient.status = status
            patient.priority_score = self._compute_priority_score(patient)
            self._persist_patient(patient)
            return patient

    def delete_patient(self, patient_id: str) -> bool:
        with self._lock:
            if patient_id in self._patients:
                del self._patients[patient_id]
                return True
            return False

    # ── Alerts ───────────────────────────────────────────────────────────────────
    def add_alert(self, alert: AlertEvent):
        with self._lock:
            # Don't duplicate alerts for same patient if already active
            existing = [a for a in self._alerts if a.patient_id == alert.patient_id and not a.acknowledged]
            if not existing:
                self._alerts.append(alert)
                self._persist_alert(alert)

    def get_alerts(self, unacknowledged_only: bool = False) -> List[AlertEvent]:
        with self._lock:
            if unacknowledged_only:
                return [a for a in self._alerts if not a.acknowledged]
            return list(self._alerts)

    def acknowledge_alert(self, alert_id: str) -> bool:
        with self._lock:
            for alert in self._alerts:
                if alert.alert_id == alert_id:
                    alert.acknowledged = True
                    return True
            return False

    # ── Stats ────────────────────────────────────────────────────────────────────
    def get_stats(self) -> dict:
        active = self.get_active_patients()
        return {
            "total": len(active),
            "critical": sum(1 for p in active if p.severity == SeverityLevel.CRITICAL),
            "urgent": sum(1 for p in active if p.severity == SeverityLevel.URGENT),
            "minor": sum(1 for p in active if p.severity == SeverityLevel.MINOR),
            "unacknowledged_alerts": len(self.get_alerts(unacknowledged_only=True)),
        }


# ── Singleton ────────────────────────────────────────────────────────────────────
store = MemoryStore()
