from typing import List, Dict, Any

class ContextBuilder:
    @staticmethod
    def format_timeline(frames: List[Dict[str, Any]]) -> str:
        lines = []
        for f in frames:
            ts = f.get("timestamp", "")
            loc = f.get("location_tag", "")
            desc = f.get("description", "")
            alert = f" [ALERT: {f.get('alert_severity')}]" if f.get("alert_severity") else ""
            lines.append(f"- {ts} @ {loc}: {desc}{alert}")
        return "\n".join(lines) if lines else "No frames recorded."

    @staticmethod
    def format_events(events: List[Dict[str, Any]]) -> str:
        lines = []
        for e in events:
            label = e.get("label", "Entity")
            count = e.get("occurrence_count", 1)
            locs = ", ".join(e.get("locations", []))
            first = e.get("first_seen", "")
            last = e.get("last_seen", "")
            lines.append(f"- {label}: Spotted {count} time(s). Locations: [{locs}]. First seen: {first}, Last seen: {last}.")
        return "\n".join(lines) if lines else "No tracked entity profiles."

    @staticmethod
    def format_alerts(alerts: List[Dict[str, Any]]) -> str:
        lines = []
        for a in alerts:
            ts = a.get("timestamp", "")
            sev = a.get("severity", "")
            msg = a.get("message", "")
            rec = a.get("recommended_action", "")
            lines.append(f"- [{sev}] {ts}: {msg} -> Action: {rec}")
        return "\n".join(lines) if lines else "No active alerts."
