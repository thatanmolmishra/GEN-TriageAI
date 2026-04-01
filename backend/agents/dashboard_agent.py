"""
Dashboard Agent – Aggregates live queue + alerts for WebSocket broadcasts.
Runs on a background loop and pushes updates to all connected clients.
"""
from __future__ import annotations
import asyncio
from datetime import datetime

from agents.priority_queue_agent import priority_queue_agent
from agents.alert_agent import alert_agent
from config import WS_BROADCAST_INTERVAL


class DashboardAgent:
    """
    Continuously aggregates data from queue and alert agents,
    then pushes payloads to the WebSocket manager.
    """

    def __init__(self):
        self._running = False
        self._ws_manager = None  # Injected after WebSocket manager is created

    def set_ws_manager(self, manager):
        self._ws_manager = manager

    def build_queue_payload(self) -> dict:
        return {
            "type": "queue_update",
            "timestamp": datetime.utcnow().isoformat(),
            "data": priority_queue_agent.get_full_queue_payload(),
        }

    def build_alert_payload(self, alert=None) -> dict:
        """Immediate alert broadcast (triggered by new alert)."""
        return {
            "type": "alert",
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "alerts": alert_agent.get_active_alerts_payload(),
                "new_alert": (
                    {
                        "alert_id": alert.alert_id,
                        "patient_id": alert.patient_id,
                        "patient_name": alert.patient_name,
                        "severity": alert.severity,
                        "message": alert.message,
                        "triggered_at": alert.triggered_at.isoformat(),
                    }
                    if alert
                    else None
                ),
            },
        }

    def build_combined_payload(self) -> dict:
        """Full payload combining queue and alerts."""
        queue_data = priority_queue_agent.get_full_queue_payload()
        alerts_data = alert_agent.get_active_alerts_payload()
        return {
            "type": "dashboard_update",
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "queue": queue_data,
                "alerts": alerts_data,
            },
        }

    async def start_broadcast_loop(self):
        """Background task: broadcast combined updates every N seconds."""
        self._running = True
        print(f"[DashboardAgent] Starting broadcast loop every {WS_BROADCAST_INTERVAL}s")
        while self._running:
            if self._ws_manager and self._ws_manager.active_connections:
                payload = self.build_combined_payload()
                await self._ws_manager.broadcast(payload)
            await asyncio.sleep(WS_BROADCAST_INTERVAL)

    async def push_immediate(self, payload: dict):
        """Push an immediate update (e.g. new patient or critical alert)."""
        if self._ws_manager:
            await self._ws_manager.broadcast(payload)

    def stop(self):
        self._running = False


dashboard_agent = DashboardAgent()
