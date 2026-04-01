"""
WebSocket Connection Manager.
Handles connect/disconnect, and broadcasts JSON payloads to all active clients.
"""
from __future__ import annotations
import json
import asyncio
from fastapi import WebSocket
from typing import List


class WebSocketManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"[WSManager] Client connected. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        print(f"[WSManager] Client disconnected. Total: {len(self.active_connections)}")

    async def broadcast(self, payload: dict):
        """Broadcast a payload dict to all connected clients."""
        if not self.active_connections:
            return

        message = json.dumps(payload, default=str)
        disconnected = []

        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                print(f"[WSManager] Failed to send to client: {e}")
                disconnected.append(connection)

        # Clean up dead connections
        for conn in disconnected:
            self.disconnect(conn)

    async def send_to_client(self, websocket: WebSocket, payload: dict):
        """Send a message to a specific client."""
        try:
            await websocket.send_text(json.dumps(payload, default=str))
        except Exception as e:
            print(f"[WSManager] Failed to send to specific client: {e}")
            self.disconnect(websocket)

    @property
    def connection_count(self) -> int:
        return len(self.active_connections)


# Singleton
ws_manager = WebSocketManager()
