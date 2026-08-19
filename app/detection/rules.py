import uuid
from typing import List, Optional
from datetime import datetime
from app.models.frame import FramePacket
from app.models.observation import StructuredObservation
from app.models.alert import SecurityAlert, SeverityLevel
from app.models.event import TrackedEvent
from app.detection.severity import SeverityScorer
from app.core.logging import logger

class BaseRule:
    rule_id: str
    rule_name: str

    def evaluate(
        self,
        frame: FramePacket,
        observation: StructuredObservation,
        tracked_events: List[TrackedEvent]
    ) -> Optional[SecurityAlert]:
        raise NotImplementedError


class NightLoiteringRule(BaseRule):
    rule_id = "RULE-001"
    rule_name = "Nighttime Perimeter Loitering Detection"

    def evaluate(
        self,
        frame: FramePacket,
        observation: StructuredObservation,
        tracked_events: List[TrackedEvent]
    ) -> Optional[SecurityAlert]:
        hour = frame.timestamp.hour
        is_night = hour >= 22 or hour <= 5
        
        has_person = any(obj.object_type == "person" for obj in observation.objects)
        is_loitering = any(act.activity_type in ["loitering", "pacing", "unauthorized_approach"] for act in observation.activities)
        
        if is_night and has_person:
            # Check if this person was seen across multiple frames
            is_repeated = any(e.entity_type == "person" and e.occurrence_count >= 2 for e in tracked_events)
            
            risk_score, severity = SeverityScorer.calculate_risk(
                base_threat=0.45,
                is_night=True,
                is_restricted_zone=True,
                is_loitering=is_loitering,
                is_repeated_anomaly=is_repeated,
                risk_indicators=observation.risk_indicators
            )
            
            person_obj = next((o for o in observation.objects if o.object_type == "person"), None)
            desc_detail = person_obj.label if person_obj else "Individual"
            clothing = person_obj.attributes.get("clothing", "") if person_obj else ""
            clothing_str = f" in {clothing}" if clothing else ""

            msg = f"Security Alert: {desc_detail}{clothing_str} detected loitering after-hours at {frame.telemetry.location_tag} (Altitude: {frame.telemetry.altitude}m)."
            rec = "Dispatch ground security team to intercept individual and verify authorization credentials."
            
            return SecurityAlert(
                alert_id=f"ALT-{uuid.uuid4().hex[:8].upper()}",
                timestamp=frame.timestamp,
                frame_id=frame.frame_id,
                location=frame.telemetry.location_tag,
                rule_id=self.rule_id,
                rule_name=self.rule_name,
                severity=severity,
                risk_score=risk_score,
                detection_confidence=observation.vlm_confidence,
                message=msg,
                recommended_action=rec,
                metadata={
                    "hour": hour,
                    "location": frame.telemetry.location_tag,
                    "objects": [o.model_dump() for o in observation.objects],
                    "risk_indicators": observation.risk_indicators
                }
            )
        return None


class RepeatedVehicleRule(BaseRule):
    rule_id = "RULE-002"
    rule_name = "Multi-Entry Vehicle Profile Correlator"

    def evaluate(
        self,
        frame: FramePacket,
        observation: StructuredObservation,
        tracked_events: List[TrackedEvent]
    ) -> Optional[SecurityAlert]:
        for event in tracked_events:
            if event.entity_type == "vehicle" and event.occurrence_count >= 2:
                # Vehicle spotted multiple times today
                risk_score, severity = SeverityScorer.calculate_risk(
                    base_threat=0.20,
                    is_night=(frame.timestamp.hour >= 22 or frame.timestamp.hour <= 5),
                    is_restricted_zone=(frame.telemetry.location_tag == "Garage Loading Bay"),
                    is_repeated_anomaly=True,
                    risk_indicators=observation.risk_indicators
                )
                
                loc_history = " -> ".join(event.locations)
                msg = f"Vehicle Activity Profile: {event.label} observed for occurrence #{event.occurrence_count}. Trajectory: {loc_history}."
                rec = "Cross-reference vehicle license and dispatch logs with authorized visitor manifests."

                return SecurityAlert(
                    alert_id=f"ALT-{uuid.uuid4().hex[:8].upper()}",
                    timestamp=frame.timestamp,
                    frame_id=frame.frame_id,
                    location=frame.telemetry.location_tag,
                    rule_id=self.rule_id,
                    rule_name=self.rule_name,
                    severity=severity,
                    risk_score=risk_score,
                    detection_confidence=observation.vlm_confidence,
                    message=msg,
                    recommended_action=rec,
                    metadata={
                        "event_id": event.event_id,
                        "occurrence_count": event.occurrence_count,
                        "trajectory": event.locations,
                        "vehicle": event.label
                    }
                )
        return None


class RuleEngine:
    def __init__(self, rules: Optional[List[BaseRule]] = None):
        self.rules = rules or [
            NightLoiteringRule(),
            RepeatedVehicleRule(),
        ]

    def evaluate_frame(
        self,
        frame: FramePacket,
        observation: StructuredObservation,
        tracked_events: List[TrackedEvent]
    ) -> List[SecurityAlert]:
        alerts: List[SecurityAlert] = []
        for rule in self.rules:
            alert = rule.evaluate(frame, observation, tracked_events)
            if alert:
                alerts.append(alert)
                logger.warning(f"[ALERT] [{alert.severity.value}] {rule.rule_name} triggered for Frame {frame.frame_id}: {alert.message}")
        return alerts

rule_engine = RuleEngine()
