from datetime import datetime, timezone
from typing import Optional, Tuple
from app.models.frame import FramePacket
from app.core.logging import logger

class IngestionSynchronizer:
    """
    Validates and synchronizes incoming frame stream with telemetry.
    Checks for missing fields, malformed timestamps, GPS boundary validation, and clock drift.
    """
    @staticmethod
    def validate_and_sync(frame: FramePacket) -> Tuple[bool, Optional[str]]:
        if not frame.frame_id or not frame.frame_id.strip():
            return False, "Missing or invalid frame_id."
            
        if not frame.telemetry:
            return False, "Missing telemetry payload for frame."

        # GPS boundary checks
        lat = frame.telemetry.latitude
        lon = frame.telemetry.longitude
        if not (-90.0 <= lat <= 90.0) or not (-180.0 <= lon <= 180.0):
            return False, f"Invalid GPS coordinates: ({lat}, {lon})"

        # Altitude validation
        if frame.telemetry.altitude < 0.0:
            return False, f"Invalid negative altitude: {frame.telemetry.altitude}"

        # Temporal check between frame timestamp and telemetry timestamp
        time_diff = abs((frame.timestamp - frame.telemetry.timestamp).total_seconds())
        if time_diff > 5.0:
            logger.warning(f"Clock desync warning on frame {frame.frame_id}: {time_diff}s difference.")

        return True, None
