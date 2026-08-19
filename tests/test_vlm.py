import pytest
from app.ai.mock_vlm import MockVLMEngine
from app.pipeline.simulator import generate_simulated_packets

def test_mock_vlm_person_detection():
    vlm = MockVLMEngine()
    packets = generate_simulated_packets()
    # Frame 1: Person in dark hoodie
    p1 = packets[0]
    obs1 = vlm.analyze_frame(p1)
    
    assert obs1.frame_id == p1.frame_id
    assert len(obs1.objects) >= 1
    assert obs1.objects[0].object_type == "person"
    assert obs1.objects[0].attributes.get("clothing") == "dark hoodie"
    assert "after_hours" in obs1.risk_indicators

def test_mock_vlm_vehicle_detection():
    vlm = MockVLMEngine()
    packets = generate_simulated_packets()
    # Frame 4: Blue Ford F150 truck
    p4 = packets[3]
    obs4 = vlm.analyze_frame(p4)
    
    assert obs4.frame_id == p4.frame_id
    assert len(obs4.objects) >= 1
    assert obs4.objects[0].object_type == "vehicle"
    assert "ford" in obs4.objects[0].label.lower() or "f150" in obs4.objects[0].label.lower()
    assert obs4.objects[0].attributes.get("color") == "blue"
