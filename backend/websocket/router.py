"""
WebSocket router – /ws/dashboard endpoint.
On connect: sends the current full state immediately.
Then client receives broadcasts from the DashboardAgent loop.
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from websocket.manager import ws_manager
from agents.dashboard_agent import dashboard_agent

router = APIRouter()


@router.websocket("/ws/dashboard")
async def dashboard_ws(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        # Send current state immediately on connect
        payload = dashboard_agent.build_combined_payload()
        await ws_manager.send_to_client(websocket, payload)

        # Keep connection alive; all updates come from the broadcast loop
        while True:
            # Wait for client messages (heartbeat pings, acknowledgements)
            data = await websocket.receive_text()
            # Client can send: {"type": "ack_alert", "alert_id": "..."}
            import json
            try:
                msg = json.loads(data)
                if msg.get("type") == "ping":
                    await ws_manager.send_to_client(websocket, {"type": "pong"})
            except Exception:
                pass

    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
