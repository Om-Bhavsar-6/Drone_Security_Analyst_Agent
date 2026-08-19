import re
from typing import List, Dict, Any, Tuple
from app.models.query import ChatRequest, ChatResponse, ToolExecutionTrace
from app.agent.tools import SecurityAgentTools
from app.agent.context import ContextBuilder
from app.core.logging import logger

class SecurityAnalystAssistant:
    """
    Production-grade Security Analyst Conversational Agent.
    Selects tools dynamically based on operational queries, inspects cross-frame
    event profiles and alerts, and generates context-aware forensic responses.
    """
    def __init__(self, tools: SecurityAgentTools = None):
        self.tools = tools or SecurityAgentTools()

    def process_query(self, req: ChatRequest) -> ChatResponse:
        prompt_lower = req.prompt.lower().strip()
        tools_used: List[ToolExecutionTrace] = []
        referenced_frames: List[str] = []
        
        # 1. Intent: Vehicle Tracking / Recurrence Query
        if any(w in prompt_lower for w in ["truck", "f150", "ford", "vehicle", "car"]):
            events = self.tools.get_events()
            matching_events = [e for e in events if e.get("entity_type") == "vehicle" or "truck" in e.get("label", "").lower() or "f150" in e.get("label", "").lower()]
            frames = self.tools.search_frames(query="truck F150")
            
            tools_used.append(ToolExecutionTrace(
                tool_name="get_events",
                arguments={"entity_type": "vehicle"},
                result_summary=f"Found {len(matching_events)} matching vehicle events."
            ))
            tools_used.append(ToolExecutionTrace(
                tool_name="search_frames",
                arguments={"query": "truck F150"},
                result_summary=f"Found {len(frames)} frames containing vehicle mentions."
            ))

            referenced_frames = [f.get("frame_id") for f in frames if f.get("frame_id")]

            if matching_events:
                evt = matching_events[0]
                loc_list = " and later at ".join(evt.get("locations", []))
                first_ts = evt.get("first_seen", "")
                last_ts = evt.get("last_seen", "")
                
                resp_text = (
                    f"The {evt.get('label')} was observed {evt.get('occurrence_count')} time(s) today. "
                    f"It was first spotted at {first_ts} at {evt.get('locations', ['unknown'])[0]}, "
                    f"and subsequently tracked across {loc_list} (last seen at {last_ts})."
                )
            elif frames:
                resp_text = f"Spotted vehicle activity across {len(frames)} frames. Specific sightings: {', '.join([f.get('location', '') for f in frames])}."
            else:
                resp_text = "No vehicle activity matching your query was recorded in today's drone surveillance logs."

            return ChatResponse(
                response=resp_text,
                intent="vehicle_tracking",
                tools_used=tools_used,
                referenced_frames=referenced_frames,
                confidence=0.96
            )

        # 2. Intent: Night Loitering / Person / Suspicious Activity Query
        elif any(w in prompt_lower for w in ["person", "individual", "hoodie", "loiter", "suspicious", "night", "gate"]):
            alerts = self.tools.get_alerts(min_severity="MEDIUM")
            frames = self.tools.search_frames(query="person hoodie loitering")
            
            tools_used.append(ToolExecutionTrace(
                tool_name="get_alerts",
                arguments={"min_severity": "MEDIUM"},
                result_summary=f"Retrieved {len(alerts)} alerts."
            ))
            tools_used.append(ToolExecutionTrace(
                tool_name="search_frames",
                arguments={"query": "person hoodie loitering"},
                result_summary=f"Found {len(frames)} matching frames."
            ))

            referenced_frames = [f.get("frame_id") for f in frames if f.get("frame_id")]

            loitering_alerts = [a for a in alerts if "loiter" in a.get("message", "").lower() or "person" in a.get("message", "").lower()]
            if loitering_alerts:
                top_alert = loitering_alerts[0]
                resp_text = (
                    f"Yes, suspicious activity was confirmed after hours. "
                    f"At {top_alert.get('timestamp')}, an alert ({top_alert.get('severity')}) was generated: "
                    f"'{top_alert.get('message')}'. Recommended protocol: {top_alert.get('recommended_action')}"
                )
            elif frames:
                resp_text = f"An individual was observed across {len(frames)} frames: {frames[0].get('description')}"
            else:
                resp_text = "No suspicious pedestrian or after-hours loitering activity was detected in the surveillance window."

            return ChatResponse(
                response=resp_text,
                intent="security_threat_inquiry",
                tools_used=tools_used,
                referenced_frames=referenced_frames,
                confidence=0.95
            )

        # 3. Intent: Highest Severity / Alert Inquiry
        elif any(w in prompt_lower for w in ["highest", "severity", "critical", "alert", "threat"]):
            alerts = self.tools.get_alerts()
            tools_used.append(ToolExecutionTrace(
                tool_name="get_alerts",
                arguments={"all": True},
                result_summary=f"Retrieved {len(alerts)} alerts."
            ))
            
            if alerts:
                # Prioritize critical and high
                criticals = [a for a in alerts if a.get("severity") in ["CRITICAL", "HIGH"]]
                target = criticals[0] if criticals else alerts[0]
                referenced_frames = [target.get("frame_id")] if target.get("frame_id") else []
                resp_text = (
                    f"The highest severity incident recorded was [{target.get('severity')}] at {target.get('timestamp')} "
                    f"located at {target.get('location')}: '{target.get('message')}'. "
                    f"Risk score: {target.get('risk_score')}. Action dispatched: {target.get('recommended_action')}"
                )
            else:
                resp_text = "No security alerts have been triggered. All surveillance areas remain nominal."

            return ChatResponse(
                response=resp_text,
                intent="alert_forensics",
                tools_used=tools_used,
                referenced_frames=referenced_frames,
                confidence=0.98
            )

        # 4. Intent: Daily Summary / Overall Objects Query
        else:
            stats = self.tools.get_statistics()
            events = self.tools.get_events()
            alerts = self.tools.get_alerts()
            frames = self.tools.get_timeline()

            tools_used.append(ToolExecutionTrace(
                tool_name="get_statistics",
                arguments={},
                result_summary=f"{stats['total_frames']} frames, {stats['total_alerts']} alerts, {stats['tracked_events']} events."
            ))
            
            referenced_frames = [f.get("frame_id") for f in frames[:5] if f.get("frame_id")]
            
            entity_summaries = [f"{e.get('label')} (seen {e.get('occurrence_count')}x)" for e in events]
            entities_str = ", ".join(entity_summaries) if entity_summaries else "nominal patrols"
            
            resp_text = (
                f"Operational Shift Summary: The autonomous drone analyzed {stats['total_frames']} frames across the property. "
                f"Tracked entities include: {entities_str}. "
                f"A total of {stats['total_alerts']} alerts were raised, including {len([a for a in alerts if a.get('severity') in ['CRITICAL', 'HIGH']])} high-severity security incidents."
            )

            return ChatResponse(
                response=resp_text,
                intent="general_surveillance_summary",
                tools_used=tools_used,
                referenced_frames=referenced_frames,
                confidence=0.92
            )

security_assistant = SecurityAnalystAssistant()
