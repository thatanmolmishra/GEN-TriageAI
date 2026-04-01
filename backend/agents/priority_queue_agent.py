"""
Priority Queue Agent – Re-ranks the ER patient queue dynamically.
Recalculates priority scores and returns a sorted patient list.
"""
from __future__ import annotations
from typing import List
from models.patient import Patient, SeverityLevel, PatientStatus
from store.memory_store import store


class PriorityQueueAgent:
    """
    Manages the live ER queue.
    Re-ranks patients based on:
      1. Severity (Critical > Urgent > Minor)
      2. Wait time (longer wait = higher score within same severity)
      3. Confidence (low confidence → conservative bump)
      4. Time-based escalation (Minor → Urgent after 30 min wait)
    """

    def run(self) -> List[dict]:
        """
        Returns the current priority-sorted queue as a list of queue items.
        Side effect: updates priority scores in the store.
        """
        queue = store.get_priority_queue()
        return [p.to_queue_item() for p in queue]

    def get_queue_summary(self) -> dict:
        """Stats summary for dashboard header."""
        return store.get_stats()

    def get_critical_patients(self) -> List[Patient]:
        """Patients with Critical severity that haven't been treated."""
        return [
            p for p in store.get_active_patients()
            if p.severity == SeverityLevel.CRITICAL
            and p.status == PatientStatus.WAITING
        ]

    def get_full_queue_payload(self) -> dict:
        """Full payload for WebSocket broadcast."""
        queue = store.get_priority_queue()
        stats = store.get_stats()
        return {
            "stats": stats,
            "patients": [p.to_queue_item() for p in queue],
        }


priority_queue_agent = PriorityQueueAgent()
