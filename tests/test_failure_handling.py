from datetime import datetime
import pytest
from app.pipeline.processor import FrameProcessor
from app.models.frame import FramePacket
from app.models.telemetry import Telemetry

def test_duplicate_frame_idempotency(test_repos):
    processor = test_repos["processor"]
    dt = datetime(2026, 8, 18, 12, 0, 0)
    tel = Telemetry(
        drone_id="DRONE-01",
        timestamp=dt,
        latitude=18.5204,
        longitude=73.8567,
        altitude=15.0,
        location_tag="Main Gate"
    )
    packet = FramePacket(
        frame_id="FRM-IDEMP-001",
        sequence_number=1,
        timestamp=dt,
        telemetry=tel,
        raw_frame_summary="Vehicle at gate"
    )

    # First ingestion succeeds
    res1 = processor.process_frame(packet)
    assert res1["status"] == "success"

    # Second ingestion of duplicate frame is safely skipped
    res2 = processor.process_frame(packet)
    assert res2["status"] == "skipped"
    assert "Duplicate" in res2["message"]

def test_invalid_telemetry_rejection(test_repos):
    processor = test_repos["processor"]
    dt = datetime(2026, 8, 18, 12, 0, 0)
    # Negative altitude is invalid
    try:
        tel = Telemetry(
            drone_id="DRONE-01",
            timestamp=dt,
            latitude=18.5204,
            longitude=73.8567,
            altitude=-50.0,
            location_tag="Main Gate"
        )
    except Exception:
        # Pydantic validation caught it
        return

    packet = FramePacket(
        frame_id="FRM-INVALID-001",
        sequence_number=1,
        timestamp=dt,
        telemetry=tel
    )
    res = processor.process_frame(packet)
    assert res["status"] == "error"
