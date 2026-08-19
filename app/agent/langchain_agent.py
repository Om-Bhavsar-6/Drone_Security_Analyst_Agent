"""
LangChain-Integrated Drone Security Analyst Agent.
Demonstrates enterprise LangChain tool-calling workflows, context management,
and LLM agent integration for security operations.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime

try:
    from langchain_core.tools import tool, StructuredTool
    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

from app.storage.repositories import FrameRepository, AlertRepository, EventRepository
from app.search.retriever import HybridRetriever
from app.models.query import SearchRequest

class LangChainSecurityToolkit:
    """
    Exposes drone surveillance domain repositories as standard LangChain tools.
    """
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

    def get_tools(self) -> List[Any]:
        if not LANGCHAIN_AVAILABLE:
            return []

        @tool
        def search_surveillance_frames(query: str, location: Optional[str] = None) -> str:
            """Search indexed drone video frames using FTS5 full-text queries and location filters."""
            res = self.retriever.search(SearchRequest(query=query, location=location, limit=10))
            if not res.results:
                return "No matching frames found."
            lines = [f"Found {res.total_matches} frame(s):"]
            for f in res.results:
                alert_str = f" [ALERT: {f.alert_severity}]" if f.has_alert else ""
                lines.append(f"- Frame {f.frame_id} @ {f.location} ({f.timestamp.strftime('%H:%M')}): {f.description}{alert_str}")
            return "\n".join(lines)

        @tool
        def get_security_alerts(min_severity: Optional[str] = None) -> str:
            """Retrieve active security incident alerts filtered by severity (LOW, MEDIUM, HIGH, CRITICAL)."""
            alerts = self.alert_repo.get_all_alerts(min_severity=min_severity)
            if not alerts:
                return "No active security alerts recorded."
            lines = [f"Retrieved {len(alerts)} alert(s):"]
            for a in alerts:
                lines.append(f"- [{a['severity']}] {a['timestamp'][11:19]} @ {a['location']}: {a['message']} (Action: {a['recommended_action']})")
            return "\n".join(lines)

        @tool
        def get_cross_frame_events() -> str:
            """Get all stateful multi-frame entity profiles, recurrence counts, and trajectory paths."""
            events = self.event_repo.get_all_events()
            if not events:
                return "No cross-frame entity trajectories recorded."
            lines = [f"Tracked {len(events)} entity profile(s):"]
            for e in events:
                lines.append(f"- {e.label} [{e.entity_type}]: Observed {e.occurrence_count}x. Trajectory: {' -> '.join(e.locations)}. First seen {e.first_seen.strftime('%H:%M')}, last seen {e.last_seen.strftime('%H:%M')}.")
            return "\n".join(lines)

        @tool
        def get_mission_shift_summary() -> str:
            """Get high-level summary statistics of the current drone surveillance shift."""
            total_frames = self.frame_repo.get_frame_count()
            total_alerts = self.alert_repo.get_alert_count()
            events = self.event_repo.get_all_events()
            return (
                f"Surveillance Mission Status: {total_frames} frames processed, "
                f"{total_alerts} security alerts raised, {len(events)} unique entity trajectories tracked."
            )

        return [
            search_surveillance_frames,
            get_security_alerts,
            get_cross_frame_events,
            get_mission_shift_summary
        ]

langchain_toolkit = LangChainSecurityToolkit()
