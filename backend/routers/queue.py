"""
GET /api/queue – Returns the current priority-sorted patient queue.
"""
from fastapi import APIRouter
from models.patient import QueueResponse
from agents.priority_queue_agent import priority_queue_agent
from store.memory_store import store

router = APIRouter(prefix="/api", tags=["Queue"])


@router.get("/queue", response_model=QueueResponse)
def get_queue():
    """Return all active patients sorted by priority score (highest first)."""
    queue = priority_queue_agent.run()
    stats = store.get_stats()
    return QueueResponse(
        total=stats["total"],
        critical_count=stats["critical"],
        urgent_count=stats["urgent"],
        minor_count=stats["minor"],
        patients=queue,
    )
