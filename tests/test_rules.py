from datetime import datetime
import pytest
from app.detection.rules import NightLoiteringRule, RepeatedVehicleRule, RuleEngine
from app.detection.severity import SeverityScorer
from app.models.alert import SeverityLevel
from app.models.frame import FramePacket
from app.models.telemetry import Telemetry
from app.models.observation import StructuredObservation, DetectedObject, DetectedActivity
from app.models.event import TrackedEvent

def test_night_loitering_rule_triggers_alert():
    rule = NightLoiteringRule()
    dt = datetime(2026, 8, 18, 0, 1, 0)
    tel = Telemetry(drone_id="DRONE-01", timestamp=dt, latitude=18.5204, longitude=73.8567, altitude=15.0, location_tag="Main Gate")
    frame = FramePacket(frame_id="FRM-TEST-001", sequence_number=1, timestamp=dt, telemetry=tel)
    
    obs = StructuredObservation(
        frame_id="FRM-TEST-001",
        description="Person pacing near gate",
        objects=[DetectedObject(object_type="person", label="Adult", attributes={"clothing": "dark hoodie"}, confidence=0.95)],
        activities=[DetectedActivity(activity_type="loitering", confidence=0.9)],
        risk_indicators=["after_hours", "hooded_garment"],
        vlm_confidence=0.95
    )
    
    alert = rule.evaluate(frame, obs, [])
    assert alert is not None
    assert alert.severity in [SeverityLevel.HIGH, SeverityLevel.CRITICAL]
    assert alert.risk_score >= 0.60
    assert "loitering" in alert.message.lower() or "security" in alert.message.lower()

def test_severity_scorer_bounds():
    score, sev = SeverityScorer.calculate_risk(base_threat=0.5, is_night=True, is_restricted_zone=True, is_loitering=True)
    assert 0.0 <= score <= 1.0
    assert sev == SeverityLevel.CRITICAL
