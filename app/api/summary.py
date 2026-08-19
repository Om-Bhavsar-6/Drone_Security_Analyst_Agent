from fastapi import APIRouter
from app.models.query import SummaryResponse
from app.storage.repositories import FrameRepository, AlertRepository, EventRepository

router = APIRouter(tags=["Surveillance Video Summary"])

frame_repo = FrameRepository()
alert_repo = AlertRepository()
event_repo = EventRepository()

@router.get("/summary", response_model=SummaryResponse)
def get_surveillance_summary():
    """
    Bonus Feature: Automated high-level summarization of all surveillance flight frames,
    cross-frame tracked events, and triggered security alerts.
    """
    total_frames = frame_repo.get_frame_count()
    alerts = alert_repo.get_all_alerts()
    events = event_repo.get_all_events()

    critical_count = len([a for a in alerts if a.get("severity") in ["CRITICAL", "HIGH"]])
    
    key_obs = []
    for e in events:
        key_obs.append(f"{e.label} spotted {e.occurrence_count}x at {', '.join(e.locations)}")
    if not key_obs:
        key_obs.append("Routine patrol completed. No unauthorized anomalies detected.")

    summary_text = (
        f"Autonomous flight mission analyzed {total_frames} video frames. "
        f"Detected {len(events)} primary tracked entities and triggered {len(alerts)} security alerts "
        f"({critical_count} high/critical priority). "
        f"Key activities: {'; '.join(key_obs[:3])}."
    )

    return SummaryResponse(
        summary=summary_text,
        total_frames_analyzed=total_frames,
        total_events_tracked=len(events),
        total_alerts_triggered=len(alerts),
        critical_alerts_count=critical_count,
        key_observations=key_obs
    )
