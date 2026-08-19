from fastapi import APIRouter
from app.storage.repositories import EventRepository

router = APIRouter(tags=["Tracked Cross-Frame Events"])
event_repo = EventRepository()

@router.get("/events")
def get_tracked_events():
    """Fetch all cross-frame tracked entities and recurrence profiles."""
    events = event_repo.get_all_events()
    return {
        "status": "success",
        "total_events": len(events),
        "events": [e.model_dump() for e in events]
    }
