import pytest
from app.pipeline.simulator import generate_simulated_packets, SIMULATED_DATASET

def test_generate_simulated_packets():
    packets = generate_simulated_packets()
    assert len(packets) == len(SIMULATED_DATASET)
    for p in packets:
        assert p.frame_id.startswith("FRM-")
        assert p.telemetry.drone_id == "DRONE-01"
        assert p.telemetry.latitude > 0
        assert p.telemetry.longitude > 0
        assert p.telemetry.altitude > 0
        assert p.raw_frame_summary is not None
