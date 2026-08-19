from datetime import datetime
from typing import List
from app.models.telemetry import Telemetry
from app.models.frame import FramePacket

SIMULATED_DATASET = [
    {
        "frame_id": "FRM-20260818-0001",
        "seq": 1,
        "timestamp": "2026-08-18T00:01:00",
        "lat": 18.5204,
        "lon": 73.8567,
        "alt": 15.0,
        "location": "Main Gate",
        "heading": 45.0,
        "speed": 1.2,
        "desc": "A lone individual in a dark hoodie pacing back and forth near the fence line."
    },
    {
        "frame_id": "FRM-20260818-0003",
        "seq": 2,
        "timestamp": "2026-08-18T00:03:00",
        "lat": 18.5204,
        "lon": 73.8567,
        "alt": 14.5,
        "location": "Main Gate",
        "heading": 42.0,
        "speed": 0.5,
        "desc": "The same hooded individual loitering stationary near the main entrance pillar after hours."
    },
    {
        "frame_id": "FRM-20260818-0615",
        "seq": 3,
        "timestamp": "2026-08-18T06:15:00",
        "lat": 18.5206,
        "lon": 73.8569,
        "alt": 20.0,
        "location": "North Perimeter",
        "heading": 180.0,
        "speed": 4.5,
        "desc": "Clear field of view, deer grazing calmly near the tree line."
    },
    {
        "frame_id": "FRM-20260818-1200",
        "seq": 4,
        "timestamp": "2026-08-18T12:00:00",
        "lat": 18.5210,
        "lon": 73.8575,
        "alt": 12.5,
        "location": "Garage Loading Bay",
        "heading": 270.0,
        "speed": 2.1,
        "desc": "A blue Ford F150 pickup truck backing into the primary delivery garage space."
    },
    {
        "frame_id": "FRM-20260818-1430",
        "seq": 5,
        "timestamp": "2026-08-18T14:30:00",
        "lat": 18.5204,
        "lon": 73.8567,
        "alt": 15.0,
        "location": "Main Gate",
        "heading": 90.0,
        "speed": 3.8,
        "desc": "The same blue Ford F150 truck exiting through the main security gate."
    },
    {
        "frame_id": "FRM-20260818-2358",
        "seq": 6,
        "timestamp": "2026-08-18T23:58:00",
        "lat": 18.5204,
        "lon": 73.8567,
        "alt": 10.0,
        "location": "Main Gate",
        "heading": 0.0,
        "speed": 0.0,
        "desc": "Suspicious person loitering near the main entrance pillar after hours in a dark hoodie."
    }
]

def generate_simulated_packets() -> List[FramePacket]:
    """Generates typed FramePacket instances for the simulated flight feed."""
    packets = []
    for item in SIMULATED_DATASET:
        dt = datetime.fromisoformat(item["timestamp"])
        tel = Telemetry(
            drone_id="DRONE-01",
            timestamp=dt,
            latitude=item["lat"],
            longitude=item["lon"],
            altitude=item["alt"],
            location_tag=item["location"],
            heading_degrees=item["heading"],
            speed_mps=item["speed"]
        )
        packet = FramePacket(
            frame_id=item["frame_id"],
            sequence_number=item["seq"],
            timestamp=dt,
            telemetry=tel,
            image_reference=f"sim://frames/{item['frame_id']}.jpg",
            raw_frame_summary=item["desc"]
        )
        packets.append(packet)
    return packets
