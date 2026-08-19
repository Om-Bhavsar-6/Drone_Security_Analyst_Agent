from typing import List, Dict, Any, Optional
from app.models.query import SearchRequest
from app.storage.repositories import FrameRepository, AlertRepository, EventRepository
from app.search.retriever import HybridRetriever

class SecurityAgentTools:
    def __init__(
        self,
        retriever: Optional[HybridRetriever] = None,
        frame_repo: Optional[FrameRepository] = None,
        alert_repo: Optional[AlertRepository] = None,
        event_repo: Optional[EventRepository] = None
    ):
        self.retriever = retriever or HybridRetriever()
        self.frame_repo = frame_repo or FrameRepository()
        self.alert_repo = alert_repo or AlertRepository()
        self.event_repo = event_repo or EventRepository()

    def search_frames(self, query: Optional[str] = None, location: Optional[str] = None, object_type: Optional[str] = None) -> List[Dict[str, Any]]:
        req = SearchRequest(query=query, location=location, object_type=object_type, limit=20)
        res = self.retriever.search(req)
        return [item.model_dump() for item in res.results]

    def get_alerts(self, min_severity: Optional[str] = None) -> List[Dict[str, Any]]:
        return self.alert_repo.get_all_alerts(min_severity)

    def get_events(self) -> List[Dict[str, Any]]:
        events = self.event_repo.get_all_events()
        return [e.model_dump() for e in events]

    def get_timeline(self) -> List[Dict[str, Any]]:
        return self.frame_repo.get_all_frames(limit=50)

    def get_statistics(self) -> Dict[str, Any]:
        return {
            "total_frames": self.frame_repo.get_frame_count(),
            "total_alerts": self.alert_repo.get_alert_count(),
            "tracked_events": len(self.event_repo.get_all_events())
        }
