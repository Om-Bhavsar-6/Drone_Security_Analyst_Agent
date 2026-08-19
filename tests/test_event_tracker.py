import pytest
from app.detection.event_tracker import EventTracker
from app.storage.repositories import EventRepository
from app.pipeline.simulator import generate_simulated_packets
from app.ai.mock_vlm import MockVLMEngine

def test_cross_frame_truck_tracking(test_repos):
    event_repo = test_repos["event_repo"]
    tracker = EventTracker(event_repo)
    vlm = MockVLMEngine()
    packets = generate_simulated_packets()
    
    # Frame 4 (at Garage) and Frame 5 (at Main Gate) both feature the Ford F150
    p4 = packets[3]
    obs4 = vlm.analyze_frame(p4)
    tracker.process_frame_observations(p4, obs4)
    
    p5 = packets[4]
    obs5 = vlm.analyze_frame(p5)
    tracker.process_frame_observations(p5, obs5)
    
    events = event_repo.get_all_events()
    vehicle_events = [e for e in events if e.entity_type == "vehicle"]
    
    assert len(vehicle_events) == 1
    f150_evt = vehicle_events[0]
    assert f150_evt.occurrence_count == 2
    assert "Garage Loading Bay" in f150_evt.locations
    assert "Main Gate" in f150_evt.locations
