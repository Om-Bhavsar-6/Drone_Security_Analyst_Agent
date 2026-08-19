from datetime import datetime, timezone
import pytest
from app.pipeline.synchronizer import IngestionSynchronizer
from app.models.frame import FramePacket
from app.models.telemetry import Telemetry

def test_valid_packet_synchronization():
    now = datetime.now()
    tel = Telemetry(
        drone_id="DRONE-01",
        timestamp=now,
        latitude=18.5204,
        longitude=73.8567,
        altitude=15.0,
        location_tag="Main Gate"
    )
    packet = FramePacket(
        frame_id="FRM-TEST-001",
        sequence_number=1,
        timestamp=now,
        telemetry=tel
    )
    valid, err = IngestionSynchronizer.validate_and_sync(packet)
    assert valid is True
    assert err is None

def test_missing_frame_id():
    now = datetime.now()
    tel = Telemetry(
        drone_id="DRONE-01",
        timestamp=now,
        latitude=18.5204,
        longitude=73.8567,
        altitude=15.0,
        location_tag="Main Gate"
    )
    packet = FramePacket(
        frame_id="",
        sequence_number=1,
        timestamp=now,
        telemetry=tel
    )
    valid, err = IngestionSynchronizer.validate_and_sync(packet)
    assert valid is False
    assert "frame_id" in err.lower()
